from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="HARIS Gateway")
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "gateway"}


@app.get("/health/services")
def health_services() -> dict[str, str]:
    return {
        "gateway": "ok",
        "redteam": "http://redteam:8001/health",
        "blueteam": "http://blueteam:8002/health",
        "blindspot": "http://blindspot:8003/health",
        "audit": "http://audit:8004/health",
    }
