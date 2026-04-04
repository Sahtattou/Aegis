from fastapi import FastAPI

from app.db.repository import Repository

app = FastAPI(title="HARIS Audit Service")
repository = Repository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "audit"}


@app.get("/timeline")
def timeline(limit: int = 100) -> list:
    return repository.get_audit_timeline(limit=limit)
