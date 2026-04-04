from fastapi import FastAPI

from app.services.redteam.attack_generator import generate_attack

app = FastAPI(title="HARIS Red Team Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "redteam"}


@app.post("/run")
def run_redteam() -> dict[str, str]:
    attack = generate_attack()
    return {"status": "queued", "attack": str(attack)}
