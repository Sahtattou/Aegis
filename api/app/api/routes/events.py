from fastapi import APIRouter

router = APIRouter()


@router.get("")
def events() -> dict[str, str]:
    return {"events": "ok"}
