def get_audit_timeline_query() -> str:
    return "MATCH (e:AuditEvent) RETURN e ORDER BY e.timestamp DESC"
