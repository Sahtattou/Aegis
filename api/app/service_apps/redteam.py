from fastapi import FastAPI

from app.db.repository import Repository
from app.services.redteam.attack_generator import generate_attack

app = FastAPI(title="HARIS Red Team Service")
repository = Repository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "redteam"}


@app.post("/run")
def run_redteam() -> dict:
    attack = generate_attack()
    created_attack = repository.create_attack(
        attack_id=attack["id"],
        content=attack["content"],
        source=attack["source"],
    )
    repository.create_audit_event(
        event_id=f"evt-{attack['id']}",
        event_type="redteam.attack.generated",
        details=f"Attack {attack['id']} generated and persisted",
    )
    return {"status": "queued", "attack": created_attack}


@app.get("/attacks")
def list_attacks(limit: int = 20) -> dict:
    return {"items": repository.list_recent_attacks(limit=limit)}
