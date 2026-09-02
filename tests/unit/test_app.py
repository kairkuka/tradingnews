from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import create_app


def test_health_endpoint_returns_static_runtime_state() -> None:
    settings = Settings(
        environment="test",
        database_url="sqlite+pysqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        timezone="Asia/Almaty",
    )
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "news-impact-bot",
        "environment": "test",
        "timezone": "Asia/Almaty",
    }

