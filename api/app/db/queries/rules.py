def create_rule_query() -> str:
    return "CREATE (r:Rule {id: $id, pattern: $pattern}) RETURN r"
