from fastapi import APIRouter, Depends

from app.api.deps import get_redteam_agent
from app.models.redteam import RedTeamRunRequest, RedTeamRunResponse
from app.services.redteam.agent import RedTeamAgent

router = APIRouter()


@router.post("/run")
def run_redteam(
    payload: RedTeamRunRequest,
    redteam_agent: RedTeamAgent = Depends(get_redteam_agent),
) -> RedTeamRunResponse:
    return redteam_agent.run(payload)
