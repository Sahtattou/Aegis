def vector_search_query() -> str:
    return """MATCH (a:Attack) RETURN a LIMIT 10"""
