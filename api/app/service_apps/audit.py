from fastapi import Depends, FastAPI

from app.core.security import configure_app_security, require_internal_api_key
from app.db.repository import Repository

app = FastAPI(title="HARIS Audit Service")
configure_app_security(app)
repository = Repository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "audit"}


@app.get("/timeline")
def timeline(
    limit: int = 100,
    _: None = Depends(require_internal_api_key),
) -> list:
    return repository.get_audit_timeline(limit=limit)
