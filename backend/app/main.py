from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.birth_profiles import router as birth_profiles_router
from app.api.astrology import router as astrology_router
from app.api.health import router as health_router
from app.api.locations import router as locations_router
from app.api.timezones import router as timezones_router
from app.api.numerology import router as numerology_router
from app.core.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    application = FastAPI(
        title="Yaşam Kodu API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    if settings.app_env == "development":
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Accept", "Content-Type"],
        )
    application.include_router(health_router)
    application.include_router(birth_profiles_router)
    application.include_router(locations_router)
    application.include_router(timezones_router)
    application.include_router(astrology_router)
    application.include_router(numerology_router)
    return application


app = create_app()
