from functools import lru_cache
from typing import Any

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://newsimpact:newsimpact@localhost:5432/newsimpact"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    service_name: str = Field(default="news-impact-bot", alias="SERVICE_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")

    database_url: str = Field(default=DEFAULT_DATABASE_URL, alias="DATABASE_URL")
    redis_url: str = Field(default=DEFAULT_REDIS_URL, alias="REDIS_URL")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    economic_data_api_key: str | None = Field(default=None, alias="ECONOMIC_DATA_API_KEY")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    market_data_api_key: str | None = Field(default=None, alias="MARKET_DATA_API_KEY")

    timezone: str = Field(default="Asia/Almaty", alias="TIMEZONE")
    historical_years: int = Field(default=10, alias="HISTORICAL_YEARS", ge=1)
    min_sample_size: int = Field(default=20, alias="MIN_SAMPLE_SIZE", ge=1)
    strict_similarity: float = Field(default=0.80, alias="STRICT_SIMILARITY", ge=0, le=1)
    relaxed_similarity: float = Field(default=0.60, alias="RELAXED_SIMILARITY", ge=0, le=1)
    reference_price_mode: str = Field(default="previous_close", alias="REFERENCE_PRICE_MODE")

    @field_validator(
        "telegram_bot_token",
        "llm_api_key",
        "economic_data_api_key",
        "news_api_key",
        "market_data_api_key",
        mode="before",
    )
    @classmethod
    def empty_secret_to_none(cls, value: Any) -> Any:
        if value == "":
            return None
        return value

    @field_validator(
        "database_url",
        "redis_url",
        "timezone",
        "reference_price_mode",
        mode="before",
    )
    @classmethod
    def empty_string_uses_default(cls, value: Any, info: ValidationInfo) -> Any:
        if value == "":
            field_name = _validated_field_name(info)
            return cls.model_fields[field_name].default
        return value

    @field_validator("historical_years", "min_sample_size", mode="before")
    @classmethod
    def empty_int_uses_default(cls, value: Any, info: ValidationInfo) -> Any:
        if value == "":
            field_name = _validated_field_name(info)
            return cls.model_fields[field_name].default
        return value

    @field_validator("strict_similarity", "relaxed_similarity", mode="before")
    @classmethod
    def empty_float_uses_default(cls, value: Any, info: ValidationInfo) -> Any:
        if value == "":
            field_name = _validated_field_name(info)
            return cls.model_fields[field_name].default
        return value


def _validated_field_name(info: ValidationInfo) -> str:
    if info.field_name is None:
        msg = "Pydantic validation info did not include a field name"
        raise ValueError(msg)
    return info.field_name


@lru_cache
def get_settings() -> Settings:
    return Settings()
