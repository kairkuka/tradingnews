from fastapi import FastAPI
from pydantic import BaseModel

from app.config.settings import Settings, get_settings
from app.logging import configure_logging


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    timezone: str


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(service=app_settings.service_name)

    app = FastAPI(
        title="News Impact Intelligence Bot",
        version="0.1.0",
        description="Historical news impact and market reaction intelligence system.",
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=app_settings.service_name,
            environment=app_settings.environment,
            timezone=app_settings.timezone,
        )

    return app


app = create_app()

