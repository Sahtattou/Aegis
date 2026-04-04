from fastapi import FastAPI

from app.api.deps import get_redteam_agent
from app.models.redteam import RedTeamRunRequest, RedTeamRunResponse

app = FastAPI(title="HARIS Red Team Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "redteam"}


@app.post("/run")
def run_redteam(payload: RedTeamRunRequest) -> RedTeamRunResponse:
    agent = get_redteam_agent()
    return agent.run(payload)
