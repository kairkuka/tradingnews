from app.config.settings import DEFAULT_DATABASE_URL, DEFAULT_REDIS_URL, Settings


def test_blank_environment_values_do_not_break_local_startup() -> None:
    settings = Settings(
        database_url="",
        redis_url="",
        telegram_bot_token="",
        llm_api_key="",
        economic_data_api_key="",
        news_api_key="",
        market_data_api_key="",
        historical_years="",
        min_sample_size="",
        strict_similarity="",
        relaxed_similarity="",
    )

    assert settings.database_url == DEFAULT_DATABASE_URL
    assert settings.redis_url == DEFAULT_REDIS_URL
    assert settings.telegram_bot_token is None
    assert settings.llm_api_key is None
    assert settings.economic_data_api_key is None
    assert settings.news_api_key is None
    assert settings.market_data_api_key is None
    assert settings.historical_years == 10
    assert settings.min_sample_size == 20
    assert settings.strict_similarity == 0.80
    assert settings.relaxed_similarity == 0.60

