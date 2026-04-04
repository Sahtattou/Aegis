from neo4j import Query


def create_audit_event_query() -> Query:
    return Query(
        "CREATE (e:AuditEvent {id: $id, event_type: $event_type, details: $details, "
        "created_at: datetime()}) RETURN e"
    )


def get_audit_timeline_query() -> Query:
    return Query(
        "MATCH (e:AuditEvent) RETURN e ORDER BY e.created_at DESC LIMIT $limit"
    )


def create_audit_event_constraint_query() -> Query:
    return Query(
        "CREATE CONSTRAINT audit_event_id IF NOT EXISTS "
        "FOR (e:AuditEvent) REQUIRE e.id IS UNIQUE"
    )
