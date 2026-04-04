from fastapi import APIRouter

router = APIRouter()


@router.post("/approve")
def approve_rule() -> dict[str, str]:
    return {"status": "approved"}
