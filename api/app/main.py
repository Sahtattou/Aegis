import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.bootstrap import initialize_neo4j
from app.db.connection import close_driver, get_neo4j_driver, verify_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    driver = get_neo4j_driver()
    try:
        verify_connection()
        initialize_neo4j(driver)
    except Exception as exc:
        logger.warning("Startup initialization skipped: %s", exc)

    yield

    close_driver()


app = FastAPI(title="HARIS API (Legacy Monolith Entry)", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
