from fastapi import FastAPI

from app.models.detection import EvaluateRequest, EvaluateResponse
from app.services.blueteam.pipeline import run_pipeline

app = FastAPI(title="HARIS Blue Team Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blueteam"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    return run_pipeline(payload)
