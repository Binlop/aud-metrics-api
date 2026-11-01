from fastapi import FastAPI
from api.v1.router import router as v1_router
from core.lifespan import lifespan
from core.config import settings
from middleware import AccessLogMiddleware
import db.models
from analytics.deps import RespondentServiceDep
from core.logging import configure_logging
configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)
app.include_router(v1_router)

# Абсолютный путь /getPercent без разделения по версиям api
@app.get("/getPercent")
async def get_percent(
    audience1: str, 
    audience2: str,
    service: RespondentServiceDep
):
    return await service.get_percent(audience1, audience2)
    
app.add_middleware(AccessLogMiddleware)