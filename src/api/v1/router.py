from fastapi import APIRouter
from api.v1.analytics import router as analytics_router

router = APIRouter(prefix="/api/v1")
router.include_router(analytics_router)