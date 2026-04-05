from fastapi import APIRouter, Depends

from app.api.deps import get_repository
from app.db.repository import Repository
from app.models.detection import (
    EvaluateRequest,
    EvaluateResponse,
    ForensicTimelineResponse,
)
from app.services.blueteam.pipeline import run_pipeline

router = APIRouter()


@router.post("/evaluate")
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    return run_pipeline(payload)


@router.get("/forensics/{attack_id}")
def forensic_timeline(
    attack_id: str,
    repository: Repository = Depends(get_repository),
) -> ForensicTimelineResponse:
    timeline = repository.get_attack_forensic_timeline(attack_id)
    events = timeline.get("events", [])
    return ForensicTimelineResponse(
        attack_id=attack_id,
        events=events,
        total_events=int(timeline.get("total_events", 0)),
        data_completeness=str(timeline.get("data_completeness", "degraded")),
    )
