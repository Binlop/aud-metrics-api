from fastapi import APIRouter
from analytics.deps import RespondentServiceDep

router = APIRouter(prefix="/analytics", tags=["Analytics"])

class AnalyticsView:

    @router.get("/getPercent")
    async def get_percent(
        audience1: str, 
        audience2: str,
        service: RespondentServiceDep
    ):
        return await service.get_percent(audience1, audience2)