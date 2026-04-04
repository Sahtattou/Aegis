from importlib import import_module

from fastapi import APIRouter, Depends

from app.api.deps import get_redteam_agent
from app.services.redteam.agent import RedTeamAgent

router = APIRouter()


@router.post("/run")
def run_redteam(
    payload: dict,
    redteam_agent: RedTeamAgent = Depends(get_redteam_agent),
) -> dict:
    models = import_module("app.models.redteam")
    request_model = getattr(models, "RedTeamRunRequest")
    payload_model = request_model.model_validate(payload)
    response = redteam_agent.run(payload_model)
    return response.model_dump()
