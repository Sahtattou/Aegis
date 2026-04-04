from neo4j import Driver, GraphDatabase

from app.config import settings

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _driver


def verify_connection() -> bool:
    driver = get_driver()
    driver.verify_connectivity()
    return True


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
