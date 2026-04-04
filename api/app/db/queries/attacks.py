def get_attack_query() -> str:
    return "MATCH (a:Attack {id: $id}) RETURN a"
