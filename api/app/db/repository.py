from app.db.connection import get_driver, verify_connection
from app.db.queries.attacks import (
    create_attack_query,
    get_attack_query,
    list_recent_attacks_query,
)
from app.db.queries.audit import create_audit_event_query, get_audit_timeline_query


class Repository:
    def health(self) -> dict[str, str]:
        verify_connection()
        return {"db": "ready"}

    def create_attack(self, attack_id: str, content: str, source: str) -> dict:
        driver = get_driver()
        params = {"id": attack_id, "content": content, "source": source}
        with driver.session() as session:
            record = session.run(create_attack_query(), params).single()
            node = record["a"] if record is not None else None
        return dict(node) if node is not None else {}

    def get_attack(self, attack_id: str) -> dict | None:
        driver = get_driver()
        with driver.session() as session:
            record = session.run(get_attack_query(), {"id": attack_id}).single()
            node = record["a"] if record is not None else None
        return dict(node) if node is not None else None

    def list_recent_attacks(self, limit: int = 20) -> list[dict]:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(list_recent_attacks_query(), {"limit": limit})
            return [dict(record["a"]) for record in result]

    def create_audit_event(self, event_id: str, event_type: str, details: str) -> dict:
        driver = get_driver()
        params = {"id": event_id, "event_type": event_type, "details": details}
        with driver.session() as session:
            record = session.run(create_audit_event_query(), params).single()
            node = record["e"] if record is not None else None
        return dict(node) if node is not None else {}

    def get_audit_timeline(self, limit: int = 100) -> list[dict]:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(get_audit_timeline_query(), {"limit": limit})
            return [dict(record["e"]) for record in result]
