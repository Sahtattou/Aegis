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
    create_blue_detection_constraint_query,
    create_blue_evaluation_query,
    create_audit_event_constraint_query,
    create_audit_event_query,
    get_attack_forensic_timeline_query,
    get_audit_timeline_query,
)

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, neo4j_driver: Driver | None = None) -> None:
        self._driver = neo4j_driver

    def health(self) -> dict[str, str]:
        verify_connection()
        self.ensure_constraints()
        return {"db": "ready"}

    def _driver_or_none(self):
        if self._driver is not None:
            return self._driver
        try:
            return get_neo4j_driver()
        except Exception as exc:
            logger.warning("Neo4j driver unavailable: %s", exc)
            return None

    def ensure_constraints(self) -> None:
        driver = self._driver_or_none()
        if driver is None:
            return
        with driver.session() as session:
            session.run(create_audit_event_constraint_query())
            session.run(create_blue_detection_constraint_query())

    def create_attack(self, attack_id: str, content: str, source: str) -> dict:
        driver = self._driver_or_none()
        if driver is None:
            return {}
        params = {"id": attack_id, "content": content, "source": source}
        with driver.session() as session:
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
        driver = self._driver_or_none()
        if driver is None:
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
            with driver.session() as session:
                record = session.run(create_structured_attack_query(), params).single()
                node = record["a"] if record is not None else None
            return dict(node) if node is not None else {}
        except Exception as exc:
            logger.warning("Failed to persist structured attack: %s", exc)
            return {}

    def get_attack(self, attack_id: str) -> dict | None:
        driver = self._driver_or_none()
        if driver is None:
            return None
        with driver.session() as session:
            record = session.run(get_attack_query(), {"id": attack_id}).single()
            node = record["a"] if record is not None else None
        return dict(node) if node is not None else None

    def list_recent_attacks(self, limit: int = 20) -> list[dict]:
        driver = self._driver_or_none()
        if driver is None:
            return []
        with driver.session() as session:
            result = session.run(list_recent_attacks_query(), {"limit": limit})
            return [dict(record["a"]) for record in result]

    def create_audit_event(self, event_id: str, event_type: str, details: str) -> dict:
        driver = self._driver_or_none()
        if driver is None:
            return {}
        try:
            self.ensure_constraints()
            params = {"id": event_id, "event_type": event_type, "details": details}
            with driver.session() as session:
                record = session.run(create_audit_event_query(), params).single()
                node = record["e"] if record is not None else None
            return dict(node) if node is not None else {}
        except Exception as exc:
            logger.warning("Failed to persist audit event: %s", exc)
            return {}

    def get_audit_timeline(self, limit: int = 100) -> list[dict]:
        driver = self._driver_or_none()
        if driver is None:
            return []
        with driver.session() as session:
            result = session.run(get_audit_timeline_query(), {"limit": limit})
            return [dict(record["e"]) for record in result]

    def create_blue_evaluation(
        self,
        *,
        detection_id: str,
        attack_id: str,
        content: str,
        source: str | None,
        pipeline_version: str,
        ml_confidence: float,
        llm_confidence: float,
        fused_confidence: float,
        decision: str,
        threat_class: str,
        detected: bool,
        band: str,
        blind_spot: bool,
        gap_severity: str,
        payload_hash: str,
        context_ids: list[str],
        audit_event_id: str,
    ) -> dict:
        driver = self._driver_or_none()
        if driver is None:
            return {}

        params = {
            "detection_id": detection_id,
            "attack_id": attack_id,
            "content": content,
            "source": source or "unknown",
            "pipeline_version": pipeline_version,
            "ml_confidence": ml_confidence,
            "llm_confidence": llm_confidence,
            "fused_confidence": fused_confidence,
            "decision": decision,
            "threat_class": threat_class,
            "detected": detected,
            "band": band,
            "blind_spot": blind_spot,
            "gap_severity": gap_severity,
            "payload_hash": payload_hash,
            "context_ids": context_ids,
            "audit_event_id": audit_event_id,
            "audit_details": (
                f"attack_id={attack_id}; decision={decision}; threat_class={threat_class}; "
                f"fused_confidence={fused_confidence:.4f}; payload_hash={payload_hash}"
            ),
        }

        try:
            self.ensure_constraints()
            with driver.session() as session:
                record = session.run(create_blue_evaluation_query(), params).single()
                detection = record["d"] if record is not None else None
            return dict(detection) if detection is not None else {}
        except Exception as exc:
            logger.warning("Failed to persist blue evaluation: %s", exc)
            return {}

    def get_attack_forensic_timeline(self, attack_id: str) -> dict:
        driver = self._driver_or_none()
        if driver is None:
            return {
                "attack_id": attack_id,
                "events": [],
                "total_events": 0,
                "data_completeness": "degraded",
            }

        try:
            with driver.session() as session:
                result = session.run(
                    get_attack_forensic_timeline_query(),
                    {"attack_id": attack_id},
                )
                records = list(result)
        except Exception as exc:
            logger.warning("Failed to fetch forensic timeline: %s", exc)
            return {
                "attack_id": attack_id,
                "events": [],
                "total_events": 0,
                "data_completeness": "degraded",
            }

        events: list[dict] = []
        for record in records:
            detection_node = record.get("d")
            audit_node = record.get("e")
            if detection_node is None:
                continue

            detection = dict(detection_node)
            audit = dict(audit_node) if audit_node is not None else None
            events.append(
                {
                    "event_id": str(detection.get("id", "")),
                    "ts": str(detection.get("created_at", "")),
                    "event_type": "blueteam.evaluation",
                    "detection": {
                        "decision": str(detection.get("decision", "suspicious")),
                        "threat_class": str(
                            detection.get("threat_class", "suspicious")
                        ),
                        "ml_confidence": float(detection.get("ml_confidence", 0.0)),
                        "llm_confidence": float(detection.get("llm_confidence", 0.0)),
                        "fused_confidence": float(
                            detection.get("fused_confidence", 0.0)
                        ),
                        "band": str(detection.get("band", "uncertain")),
                        "blind_spot": bool(detection.get("blind_spot", False)),
                        "gap_severity": str(detection.get("gap_severity", "MEDIUM")),
                    },
                    "context_references": [
                        {
                            "type": "graph_context",
                            "id": context_id,
                        }
                        for context_id in detection.get("context_ids", [])
                    ],
                    "audit_linkage": {
                        "audit_event_id": str(
                            detection.get("audit_event_id", "unknown")
                        ),
                        "payload_hash": str(detection.get("payload_hash", "")),
                        "details": str(audit.get("details", "")) if audit else "",
                    },
                }
            )

        data_completeness = "full" if events else "degraded"
        return {
            "attack_id": attack_id,
            "events": events,
            "total_events": len(events),
            "data_completeness": data_completeness,
        }

    def max_attack_similarity(
        self, embedding: list[float], k_neighbors: int = 10
    ) -> float:
        driver = self._driver_or_none()
        if driver is None:
            return 0.0

        if settings.neo4j_password == "neo4jpassword":
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
            with driver.session() as session:
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
            logger.warning(
                "Vector index query failed, falling back to exhaustive cosine query: %s",
                exc,
            )

        try:
            with driver.session() as session:
                record = session.run(exhaustive_query, embedding=embedding).single()
                max_similarity = record["max_similarity"] if record else None
                if max_similarity is not None:
                    return max(0.0, min(1.0, float(max_similarity)))
        except Exception as exc:
            logger.warning(
                "Exhaustive cosine query failed, defaulting similarity to zero: %s", exc
            )
            return 0.0

        return 0.0
