from app.config import settings


driver = {
    "uri": settings.neo4j_uri,
    "auth": (settings.neo4j_username, settings.neo4j_password),
}
