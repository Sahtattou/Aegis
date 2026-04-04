from fastapi import APIRouter

from app.services.blueteam.rules_engine import load_rules

router = APIRouter()


@router.post("/approve")
def approve_rule() -> dict[str, str]:
    return {"status": "approved"}


@router.get("")
def list_rules() -> dict[str, int]:
    rules = load_rules()
    return {"count": len(rules)}
