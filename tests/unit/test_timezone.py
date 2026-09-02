from zoneinfo import ZoneInfo

from app.config.settings import Settings


def test_configured_timezone_is_valid() -> None:
    settings = Settings(timezone="Asia/Almaty")

    assert ZoneInfo(settings.timezone).key == "Asia/Almaty"

