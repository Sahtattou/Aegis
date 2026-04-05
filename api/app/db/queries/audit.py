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


def create_blue_detection_constraint_query() -> Query:
    return Query(
        "CREATE CONSTRAINT blue_detection_id IF NOT EXISTS "
        "FOR (d:BlueDetection) REQUIRE d.id IS UNIQUE"
    )


def create_blue_evaluation_query() -> Query:
    return Query(
        "MERGE (a:Attack {id: $attack_id}) "
        "ON CREATE SET a.content = $content, a.source = $source, a.created_at = datetime() "
        "CREATE (d:BlueDetection {"
        "id: $detection_id, "
        "attack_id: $attack_id, "
        "pipeline_version: $pipeline_version, "
        "ml_confidence: $ml_confidence, "
        "llm_confidence: $llm_confidence, "
        "fused_confidence: $fused_confidence, "
        "decision: $decision, "
        "threat_class: $threat_class, "
        "detected: $detected, "
        "band: $band, "
        "blind_spot: $blind_spot, "
        "gap_severity: $gap_severity, "
        "payload_hash: $payload_hash, "
        "context_ids: $context_ids, "
        "audit_event_id: $audit_event_id, "
        "created_at: datetime()"
        "}) "
        "MERGE (e:AuditEvent {id: $audit_event_id}) "
        "ON CREATE SET e.event_type = 'blueteam_evaluation', e.details = $audit_details, e.created_at = datetime() "
        "ON MATCH SET e.event_type = 'blueteam_evaluation', e.details = $audit_details "
        "MERGE (a)-[:HAS_BLUE_DETECTION]->(d) "
        "MERGE (d)-[:HAS_AUDIT_EVENT]->(e) "
        "RETURN a, d, e"
    )


def get_attack_forensic_timeline_query() -> Query:
    return Query(
        "MATCH (a:Attack {id: $attack_id}) "
        "OPTIONAL MATCH (a)-[:HAS_BLUE_DETECTION]->(d:BlueDetection) "
        "OPTIONAL MATCH (d)-[:HAS_AUDIT_EVENT]->(e:AuditEvent) "
        "RETURN a, d, e "
        "ORDER BY d.created_at DESC"
    )
