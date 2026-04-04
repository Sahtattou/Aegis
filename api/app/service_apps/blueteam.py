from fastapi import FastAPI

from app.services.blueteam.pipeline import run_pipeline

app = FastAPI(title="HARIS Blue Team Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blueteam"}


@app.post("/evaluate")
def evaluate(payload: dict) -> dict:
    return run_pipeline(payload)
