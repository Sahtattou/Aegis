from functools import lru_cache

from neo4j import Driver, GraphDatabase

from app.config import settings


@lru_cache(maxsize=1)
def get_neo4j_driver() -> Driver:
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
        connection_timeout=settings.neo4j_connection_timeout_seconds,
        connection_acquisition_timeout=settings.neo4j_acquisition_timeout_seconds,
    )


def verify_connection() -> bool:
    driver = get_neo4j_driver()
    driver.verify_connectivity()
    return True


def close_driver() -> None:
    get_neo4j_driver().close()
    get_neo4j_driver.cache_clear()
