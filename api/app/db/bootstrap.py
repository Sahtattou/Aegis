from __future__ import annotations

import logging
from hashlib import sha256
from pathlib import Path

from neo4j import Driver

from app.config import settings

logger = logging.getLogger(__name__)


def _embedding_from_seed(seed: str, dimensions: int) -> list[float]:
    digest = sha256(seed.encode("utf-8")).digest()
    return [digest[index % len(digest)] / 255.0 for index in range(dimensions)]


def _split_cypher_statements(script_content: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []

    for raw_line in script_content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("//"):
            continue

        current.append(raw_line)
        if line.endswith(";"):
            statement = "\n".join(current).strip()
            statement = statement[:-1].strip() if statement.endswith(";") else statement
            if statement:
                statements.append(statement)
            current = []

    trailing = "\n".join(current).strip()
    if trailing:
        statements.append(trailing)

    return statements


def run_init_scripts(driver: Driver) -> None:
    init_dir = Path(settings.neo4j_init_dir)
    if not init_dir.exists():
        logger.warning("Neo4j init directory not found: %s", init_dir)
        return

    script_paths = sorted(init_dir.glob("*.cypher"))
    if not script_paths:
        logger.warning("No Neo4j init scripts found in %s", init_dir)
        return

    with driver.session() as session:
        for script_path in script_paths:
            script_content = script_path.read_text(encoding="utf-8")
            for statement in _split_cypher_statements(script_content):
                session.run(statement).consume()


def bootstrap_kb_collections(driver: Driver) -> None:
    collections = [
        {
            "collection": "ANCS",
            "chunk_id": "ancs-001",
            "title": "ANCS advisory baseline",
            "content": "ANCS and tunCERT advisories focusing on phishing, credential abuse, and social engineering targeting Tunisian entities.",
            "source": "ANCS/tunCERT",
        },
        {
            "collection": "MITRE",
            "chunk_id": "mitre-001",
            "title": "MITRE ATT&CK baseline",
            "content": "MITRE ATT&CK techniques relevant to phishing, valid account abuse, and credential access patterns.",
            "source": "MITRE ATT&CK",
        },
        {
            "collection": "Tunisian signatures",
            "chunk_id": "tn-sign-001",
            "title": "Tunisian threat signatures",
            "content": "Tunisian signatures in Darija, Arabic, and French involving Poste Tunisienne, BIAT, STB, Tunisie Telecom, and Ooredoo impersonation.",
            "source": "HARIS Tunisian Signatures",
        },
    ]

    create_collection_query = """
MERGE (kc:KnowledgeCollection {name: $collection})
ON CREATE SET kc.created_at = datetime()
SET kc.updated_at = datetime()
WITH kc
MERGE (k:KnowledgeChunk {id: $chunk_id})
SET k.collection = $collection,
    k.title = $title,
    k.content = $content,
    k.source = $source,
    k.embedding = $embedding,
    k.updated_at = datetime()
ON CREATE SET k.created_at = datetime()
MERGE (k)-[:BELONGS_TO]->(kc)
"""

    create_vector_index_query = f"""
CREATE VECTOR INDEX kb_embedding_index IF NOT EXISTS
FOR (k:KnowledgeChunk)
ON (k.embedding)
OPTIONS {{
  indexConfig: {{
    `vector.dimensions`: {settings.redteam_vector_dimensions},
    `vector.similarity_function`: 'cosine'
  }}
}}
"""

    with driver.session() as session:
        for item in collections:
            embedding = _embedding_from_seed(
                seed=f"{item['collection']}|{item['title']}|{item['content']}",
                dimensions=settings.redteam_vector_dimensions,
            )
            params = {**item, "embedding": embedding}
            session.run(create_collection_query, params).consume()

        session.run(create_vector_index_query).consume()


def initialize_neo4j(driver: Driver) -> None:
    if not settings.neo4j_init_on_startup:
        logger.info("Neo4j initialization on startup disabled by configuration")
        return

    try:
        run_init_scripts(driver)
        bootstrap_kb_collections(driver)
        logger.info("Neo4j initialization completed")
    except Exception as exc:
        logger.warning("Neo4j initialization failed: %s", exc)
