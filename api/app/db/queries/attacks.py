from neo4j import Query


def create_attack_query() -> Query:
    return Query(
        "CREATE (a:Attack {id: $id, content: $content, source: $source, "
        "created_at: datetime()}) RETURN a"
    )


def get_attack_query() -> Query:
    return Query("MATCH (a:Attack {id: $id}) RETURN a LIMIT 1")


def list_recent_attacks_query() -> Query:
    return Query("MATCH (a:Attack) RETURN a ORDER BY a.created_at DESC LIMIT $limit")
