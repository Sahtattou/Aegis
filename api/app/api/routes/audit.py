from fastapi import APIRouter

router = APIRouter()


@router.get("/timeline")
def timeline() -> list:
    return []
