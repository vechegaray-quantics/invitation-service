from fastapi import FastAPI

from app.api.campaign_audiences import router as campaign_audiences_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(campaign_audiences_router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": settings.app_version,
    }


@app.get("/")
def root() -> dict:
    return {"message": "Invitation Service is running"}