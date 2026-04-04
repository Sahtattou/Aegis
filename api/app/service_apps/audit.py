from fastapi import FastAPI

app = FastAPI(title="HARIS Audit Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "audit"}


@app.get("/timeline")
def timeline() -> list:
    return []
