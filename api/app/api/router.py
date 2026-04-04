from fastapi import APIRouter

from app.api.routes import audit, blueteam, events, redteam, rules

api_router = APIRouter(prefix="/api")
api_router.include_router(redteam.router, prefix="/redteam", tags=["redteam"])
api_router.include_router(blueteam.router, prefix="/blueteam", tags=["blueteam"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
