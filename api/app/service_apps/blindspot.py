from fastapi import Depends, FastAPI

from app.core.security import configure_app_security, require_internal_api_key
from app.services.blindspot.analyzer import analyze

app = FastAPI(title="HARIS Blind Spot Service")
configure_app_security(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blindspot"}


@app.post("/analyze")
def run_blindspot(_: None = Depends(require_internal_api_key)) -> dict[str, str]:
    return analyze()
