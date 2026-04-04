from app.db.connection import get_neo4j_driver
from app.db.repository import Repository
from app.services.redteam.agent import RedTeamAgent


def get_db() -> None:
    return None


def get_repository() -> Repository:
    return Repository(get_neo4j_driver())


def get_redteam_agent() -> RedTeamAgent:
    return RedTeamAgent(get_repository())
