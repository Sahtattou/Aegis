from fastapi import Depends, FastAPI

from app.services.blueteam.pipeline import run_pipeline
from app.core.security import configure_app_security, require_internal_api_key
from app.models.detection import EvaluateRequest, EvaluateResponse

app = FastAPI(title="HARIS Blue Team Service")
configure_app_security(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blueteam"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(
    payload: EvaluateRequest,
    _: None = Depends(require_internal_api_key),
) -> EvaluateResponse:
    return run_pipeline(payload)
