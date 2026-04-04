from fastapi import APIRouter

from app.models.detection import EvaluateRequest, EvaluateResponse
from app.services.blueteam.pipeline import run_pipeline

router = APIRouter()


@router.post("/evaluate")
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    return run_pipeline(payload)
