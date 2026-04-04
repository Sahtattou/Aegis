from fastapi import APIRouter, Depends

from app.api.deps import get_repository
from app.db.repository import Repository

router = APIRouter()


@router.get("/timeline")
def timeline(
    limit: int = 100, repository: Repository = Depends(get_repository)
) -> list:
    return repository.get_audit_timeline(limit=limit)
