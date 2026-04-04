from __future__ import annotations

import os
import json
import re
import html
from pathlib import Path
from typing import Any

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None


ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = ROOT / "data" / "kb"
ANCS_FOLDER = KB_ROOT / "ancs"
TUNCERT_FOLDER = KB_ROOT / "tuncert"
MITRE_FILE = KB_ROOT / "mitre" / "enterprise-attack.json"

ANCS_URLS = {
    "ancs_home.html": "https://www.ancs.tn/",
    "ancs_alertes_de_securite.html": "https://www.ancs.tn/fr/alertes-de-securite",
    "ancs_actualites_list.html": "https://www.ancs.tn/fr/actualites",
    "ancs_tuncert.html": "https://www.ancs.tn/fr/tuncert",
    "ancs_vulnerabilites.html": "https://www.ancs.tn/fr/vulnerabilites",
}

TUNCERT_URLS = {
    "financialcert_home.html": "https://www.financialcert.tn/",
    "financialcert_actualites.html": "https://www.financialcert.tn/actualites/",
    "financialcert_alertes.html": "https://www.financialcert.tn/alerte-2/",
    "financialcert_bulletin_securite.html": "https://www.financialcert.tn/bulletin-de-securite-2/",
    "first_tuncert_profile.html": "https://www.first.org/members/teams/tuncert",
}

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style).*?</\1>", re.IGNORECASE | re.DOTALL)
WHITESPACE_RE = re.compile(r"\s+")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
MAX_BODY_CHARS = 2500


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def html_to_text(html_content: str) -> str:
    no_script = SCRIPT_STYLE_RE.sub(" ", html_content)
    no_tags = TAG_RE.sub(" ", no_script)
    clean = WHITESPACE_RE.sub(" ", no_tags).strip()
    clean = html.unescape(clean)
    return clean


def extract_title(html_content: str, fallback: str) -> str:
    m = TITLE_RE.search(html_content)
    if not m:
        return fallback
    title = WHITESPACE_RE.sub(" ", m.group(1)).strip()
    title = html.unescape(title)
    return title or fallback


def build_html_record(
    file_path: Path, source: str, url_map: dict[str, str]
) -> dict[str, Any]:
    html = read_text(file_path)
    body_text = html_to_text(html)
    if len(body_text) > MAX_BODY_CHARS:
        body_text = body_text[:MAX_BODY_CHARS]
    return {
        "doc_id": f"{source}:{file_path.stem}",
        "source": source,
        "path": str(file_path),
        "filename": file_path.name,
        "url": url_map.get(file_path.name, ""),
        "title": extract_title(html, file_path.stem),
        "body_text": body_text,
        "content_type": "text/html",
    }


def iter_source_files(folder: Path) -> list[Path]:
    files = [
        p
        for p in folder.glob("*.html")
        if p.is_file() and not p.name.lower().startswith("readme")
    ]
    files.sort()
    return files


def load_ancs() -> list[dict[str, Any]]:
    return [
        build_html_record(f, "ancs", ANCS_URLS) for f in iter_source_files(ANCS_FOLDER)
    ]


def load_tuncert() -> list[dict[str, Any]]:
    return [
        build_html_record(f, "tuncert", TUNCERT_URLS)
        for f in iter_source_files(TUNCERT_FOLDER)
    ]


def load_mitre_stix() -> dict[str, Any]:
    if not MITRE_FILE.exists():
        return {}
    with MITRE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def first_attack_external_id(obj: dict[str, Any]) -> str:
    refs = obj.get("external_references", [])
    if not isinstance(refs, list):
        return ""
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        if ref.get("source_name") in {
            "mitre-attack",
            "mitre-mobile-attack",
            "mitre-ics-attack",
        }:
            ext = ref.get("external_id")
            if isinstance(ext, str):
                return ext
    return ""


def map_mitre_objects(mitre_json: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    objects = mitre_json.get("objects", [])
    if not isinstance(objects, list):
        return {"entities": [], "relationships": []}

    max_objects_raw = os.getenv("MITRE_MAX_OBJECTS", "6000")
    try:
        max_objects = int(max_objects_raw)
    except ValueError:
        max_objects = 6000
    if max_objects < 0:
        max_objects = 0
    selected = objects[:max_objects]

    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    for obj in selected:
        if not isinstance(obj, dict):
            continue
        stix_id = obj.get("id")
        stix_type = obj.get("type")
        if not isinstance(stix_id, str) or not isinstance(stix_type, str):
            continue
        if stix_type == "relationship":
            src = obj.get("source_ref")
            dst = obj.get("target_ref")
            rel_type = obj.get("relationship_type")
            if isinstance(src, str) and isinstance(dst, str):
                relationships.append(
                    {
                        "id": stix_id,
                        "source_ref": src,
                        "target_ref": dst,
                        "relationship_type": rel_type
                        if isinstance(rel_type, str)
                        else "related-to",
                    }
                )
            continue

        entities.append(
            {
                "stix_id": stix_id,
                "stix_type": stix_type,
                "name": obj.get("name") if isinstance(obj.get("name"), str) else "",
                "description": obj.get("description")
                if isinstance(obj.get("description"), str)
                else "",
                "external_id": first_attack_external_id(obj),
                "revoked": bool(obj.get("revoked", False)),
                "x_mitre_deprecated": bool(obj.get("x_mitre_deprecated", False)),
            }
        )

    entity_ids = {e["stix_id"] for e in entities if isinstance(e.get("stix_id"), str)}
    filtered_relationships = [
        r
        for r in relationships
        if r["source_ref"] in entity_ids and r["target_ref"] in entity_ids
    ]

    return {"entities": entities, "relationships": filtered_relationships}


def chunked(rows: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def neo4j_connection() -> tuple[str, str, str]:
    uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
    return uri, user, password


def upsert_documents(tx: Any, docs: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (d:Document {doc_id: row.doc_id})
        SET d.title = row.title,
            d.url = row.url,
            d.path = row.path,
            d.body_text = row.body_text,
            d.content_type = row.content_type,
            d.updated_at = datetime()
        MERGE (s:Source {name: row.source})
        MERGE (s)-[:PUBLISHES]->(d)
        """,
        rows=docs,
    )


def upsert_entities(tx: Any, entities: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (e:MitreEntity {stix_id: row.stix_id})
        SET e.stix_type = row.stix_type,
            e.name = row.name,
            e.description = row.description,
            e.external_id = row.external_id,
            e.revoked = row.revoked,
            e.deprecated = row.x_mitre_deprecated,
            e.updated_at = datetime()
        """,
        rows=entities,
    )


def upsert_relationships(tx: Any, relationships: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (src:MitreEntity {stix_id: row.source_ref})
        MATCH (dst:MitreEntity {stix_id: row.target_ref})
        MERGE (src)-[r:RELATED_TO {stix_rel_id: row.id}]->(dst)
        SET r.relationship_type = row.relationship_type,
            r.updated_at = datetime()
        """,
        rows=relationships,
    )


def ensure_constraints(tx: Any) -> None:
    tx.run(
        """
        CREATE CONSTRAINT document_doc_id_unique IF NOT EXISTS
        FOR (d:Document) REQUIRE d.doc_id IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT source_name_unique IF NOT EXISTS
        FOR (s:Source) REQUIRE s.name IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT mitre_entity_stix_id_unique IF NOT EXISTS
        FOR (e:MitreEntity) REQUIRE e.stix_id IS UNIQUE
        """
    )


def upsert_to_neo4j(records: dict[str, Any]) -> None:
    if GraphDatabase is None:
        print("Neo4j driver not available. Skipping DB upsert.")
        return

    uri, user, password = neo4j_connection()
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        try:
            driver.verify_connectivity()
        except Exception as exc:
            print(f"Neo4j upsert skipped due to connection/auth error: {exc}")
            return

        docs = records.get("documents", [])
        entities = records.get("mitre", {}).get("entities", [])
        relationships = records.get("mitre", {}).get("relationships", [])

        with driver.session() as session:
            session.execute_write(ensure_constraints)

        try:
            with driver.session() as session:
                for batch in chunked(docs, 200):
                    session.execute_write(upsert_documents, batch)
            with driver.session() as session:
                for batch in chunked(entities, 500):
                    session.execute_write(upsert_entities, batch)
            with driver.session() as session:
                for batch in chunked(relationships, 500):
                    session.execute_write(upsert_relationships, batch)
        except Exception as exc:
            print(f"Neo4j upsert failed during write phase: {exc}")
            raise

        print(
            "Neo4j upsert completed:",
            f"documents={len(docs)}",
            f"entities={len(entities)}",
            f"relationships={len(relationships)}",
        )


def main() -> None:
    ancs_records = load_ancs()
    tuncert_records = load_tuncert()
    mitre_json = load_mitre_stix()
    mitre_mapped = map_mitre_objects(mitre_json)

    print(f"ANCS files detected: {len(ancs_records)}")
    print(f"tunCERT files detected: {len(tuncert_records)}")
    print(f"MITRE top-level keys: {list(mitre_json.keys())[:10]}")
    print(f"MITRE entities mapped: {len(mitre_mapped['entities'])}")
    print(f"MITRE relationships mapped: {len(mitre_mapped['relationships'])}")

    docs = ancs_records + tuncert_records
    payload = {
        "documents": docs,
        "mitre": mitre_mapped,
    }

    preview_payload = {
        "documents_preview": docs[:3],
        "mitre_preview": {
            "type": mitre_json.get("type"),
            "id": mitre_json.get("id"),
            "objects_count": len(mitre_json.get("objects", []))
            if isinstance(mitre_json.get("objects"), list)
            else 0,
            "entities_mapped": len(mitre_mapped["entities"]),
            "relationships_mapped": len(mitre_mapped["relationships"]),
        },
    }

    print("Preview payload:")
    print(json.dumps(preview_payload, ensure_ascii=False, indent=2))

    upsert_to_neo4j(payload)


if __name__ == "__main__":
    main()
