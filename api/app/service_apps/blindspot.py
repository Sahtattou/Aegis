from fastapi import FastAPI

from app.services.blindspot.analyzer import analyze

app = FastAPI(title="HARIS Blind Spot Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blindspot"}


@app.post("/analyze")
def run_blindspot() -> dict[str, str]:
    return analyze()
