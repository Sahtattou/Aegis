import logging

from neo4j import Driver

from app.config import settings
from app.db.connection import get_neo4j_driver, verify_connection
from app.db.queries.attacks import (
    create_attack_query,
    create_structured_attack_query,
    get_attack_query,
    list_recent_attacks_query,
)
from app.db.queries.audit import (
    create_audit_event_constraint_query,
    create_audit_event_query,
    get_audit_timeline_query,
)

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, neo4j_driver: Driver | None = None) -> None:
        self._driver = neo4j_driver or get_neo4j_driver()

    def health(self) -> dict[str, str]:
        verify_connection()
        self.ensure_constraints()
        return {"db": "ready"}

    def ensure_constraints(self) -> None:
        driver = get_driver()
        with driver.session() as session:
            session.run(create_audit_event_constraint_query())

    def create_attack(self, attack_id: str, content: str, source: str) -> dict:
        if not self._driver:
            return {}
        params = {"id": attack_id, "content": content, "source": source}
        with self._driver.session() as session:
            record = session.run(create_attack_query(), params).single()
            node = record["a"] if record is not None else None
        return dict(node) if node is not None else {}

    def create_structured_attack(
        self,
        *,
        attack_id: str,
        content: str,
        source: str,
        persona: str,
        severity: str,
        techniques: list[str],
        target: str,
        objective: str,
        embedding: list[float],
    ) -> dict:
        if not self._driver:
            return {}
        params = {
            "id": attack_id,
            "content": content,
            "source": source,
            "persona": persona,
            "severity": severity,
            "techniques": techniques,
            "target": target,
            "objective": objective,
            "embedding": embedding,
        }
        try:
            with self._driver.session() as session:
                record = session.run(create_structured_attack_query(), params).single()
                node = record["a"] if record is not None else None
            return dict(node) if node is not None else {}
        except Exception as exc:
            logger.warning("Failed to persist structured attack: %s", exc)
            return {}

    def get_attack(self, attack_id: str) -> dict | None:
        if not self._driver:
            return None
        with self._driver.session() as session:
            record = session.run(get_attack_query(), {"id": attack_id}).single()
            node = record["a"] if record is not None else None
        return dict(node) if node is not None else None

    def list_recent_attacks(self, limit: int = 20) -> list[dict]:
        if not self._driver:
            return []
        with self._driver.session() as session:
            result = session.run(list_recent_attacks_query(), {"limit": limit})
            return [dict(record["a"]) for record in result]

    def create_audit_event(self, event_id: str, event_type: str, details: str) -> dict:
        if not self._driver:
            return {}
        self.ensure_constraints()
        driver = get_driver()
        params = {"id": event_id, "event_type": event_type, "details": details}
        with self._driver.session() as session:
            record = session.run(create_audit_event_query(), params).single()
            node = record["e"] if record is not None else None
        return dict(node) if node is not None else {}

    def get_audit_timeline(self, limit: int = 100) -> list[dict]:
        if not self._driver:
            return []
        with self._driver.session() as session:
            result = session.run(get_audit_timeline_query(), {"limit": limit})
            return [dict(record["e"]) for record in result]

    def max_attack_similarity(self, embedding: list[float], k_neighbors: int = 10) -> float:
        if not self._driver:
            return 0.0

        vector_query = """
CALL db.index.vector.queryNodes($index_name, $k, $embedding)
YIELD node, score
RETURN max(score) AS max_similarity
"""
        exhaustive_query = """
MATCH (a:Attack)
WHERE a.embedding IS NOT NULL
WITH vector.similarity.cosine($embedding, a.embedding) AS score
RETURN max(score) AS max_similarity
"""

        try:
            with self._driver.session() as session:
                record = session.run(
                    vector_query,
                    index_name=settings.redteam_vector_index_name,
                    k=k_neighbors,
                    embedding=embedding,
                ).single()
                max_similarity = record["max_similarity"] if record else None
                if max_similarity is not None:
                    return max(0.0, min(1.0, float(max_similarity)))
        except Exception as exc:
            logger.warning("Vector index query failed, falling back to exhaustive cosine query: %s", exc)

        try:
            with self._driver.session() as session:
                record = session.run(exhaustive_query, embedding=embedding).single()
                max_similarity = record["max_similarity"] if record else None
                if max_similarity is not None:
                    return max(0.0, min(1.0, float(max_similarity)))
        except Exception as exc:
            logger.warning("Exhaustive cosine query failed, defaulting similarity to zero: %s", exc)
            return 0.0

        return 0.0
