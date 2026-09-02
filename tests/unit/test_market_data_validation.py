from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.config.market_data import SUPPORTED_TIMEFRAMES, require_supported_timeframe
from app.providers.market.schemas import (
    MarketDataValidationError,
    OhlcvBar,
    Quote,
    validate_ohlcv_bar,
    validate_quote,
)


def test_timeframe_registry_matches_phase_2_scope() -> None:
    assert SUPPORTED_TIMEFRAMES == ("1m", "5m", "15m", "30m", "1h", "2h", "4h", "1D")
    assert require_supported_timeframe("1d") == "1D"


def test_ohlcv_validation_normalizes_utc_timestamp() -> None:
    astana_time = datetime(2026, 9, 2, 18, 0, tzinfo=timezone(timedelta(hours=5)))
    bar = OhlcvBar(
        symbol="xauusd",
        timeframe="1d",
        timestamp=astana_time,
        open=Decimal("2500"),
        high=Decimal("2510"),
        low=Decimal("2490"),
        close=Decimal("2505"),
        volume=Decimal("100"),
    )

    validated = validate_ohlcv_bar(bar)

    assert validated.symbol == "XAUUSD"
    assert validated.timeframe == "1D"
    assert validated.timestamp == datetime(2026, 9, 2, 13, 0, tzinfo=UTC)


def test_ohlcv_validation_rejects_naive_timestamp() -> None:
    bar = OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=datetime(2026, 9, 2, 13, 0),
        open=Decimal("2500"),
        high=Decimal("2510"),
        low=Decimal("2490"),
        close=Decimal("2505"),
        volume=None,
    )

    with pytest.raises(MarketDataValidationError, match="timezone-aware UTC"):
        validate_ohlcv_bar(bar)


def test_ohlcv_validation_rejects_invalid_price_shape() -> None:
    bar = OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        open=Decimal("2500"),
        high=Decimal("2499"),
        low=Decimal("2490"),
        close=Decimal("2505"),
        volume=None,
    )

    with pytest.raises(MarketDataValidationError, match="high"):
        validate_ohlcv_bar(bar)


def test_quote_validation_rejects_crossed_market() -> None:
    quote = Quote(
        symbol="EURUSD",
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        bid=Decimal("1.1002"),
        ask=Decimal("1.1000"),
        last=Decimal("1.1001"),
    )

    with pytest.raises(MarketDataValidationError, match="bid"):
        validate_quote(quote)

