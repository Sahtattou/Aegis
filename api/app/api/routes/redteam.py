from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
def run_redteam() -> dict[str, str]:
    return {"status": "queued"}
