from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal

from app.config.assets import require_supported_symbol
from app.config.market_data import require_supported_timeframe


class MarketDataValidationError(ValueError):
    """Raised when market data cannot be trusted for ingestion."""


@dataclass(frozen=True)
class OhlcvBar:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None


@dataclass(frozen=True)
class Quote:
    symbol: str
    timestamp: datetime
    bid: Decimal | None
    ask: Decimal | None
    last: Decimal


def ensure_utc_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        msg = "Market data timestamp must be timezone-aware UTC"
        raise MarketDataValidationError(msg)
    return timestamp.astimezone(UTC)


def validate_ohlcv_bar(bar: OhlcvBar) -> OhlcvBar:
    symbol = require_supported_symbol(bar.symbol)
    timeframe = require_supported_timeframe(bar.timeframe)
    timestamp = ensure_utc_timestamp(bar.timestamp)

    _validate_non_negative("open", bar.open)
    _validate_non_negative("high", bar.high)
    _validate_non_negative("low", bar.low)
    _validate_non_negative("close", bar.close)
    if bar.volume is not None:
        _validate_non_negative("volume", bar.volume)

    if bar.high < max(bar.open, bar.close, bar.low):
        msg = "OHLCV high must be greater than or equal to open, low, and close"
        raise MarketDataValidationError(msg)
    if bar.low > min(bar.open, bar.close, bar.high):
        msg = "OHLCV low must be less than or equal to open, high, and close"
        raise MarketDataValidationError(msg)

    return replace(bar, symbol=symbol, timeframe=timeframe, timestamp=timestamp)


def validate_quote(quote: Quote) -> Quote:
    symbol = require_supported_symbol(quote.symbol)
    timestamp = ensure_utc_timestamp(quote.timestamp)

    _validate_non_negative("last", quote.last)
    if quote.bid is not None:
        _validate_non_negative("bid", quote.bid)
    if quote.ask is not None:
        _validate_non_negative("ask", quote.ask)
    if quote.bid is not None and quote.ask is not None and quote.bid > quote.ask:
        msg = "Quote bid must be less than or equal to ask"
        raise MarketDataValidationError(msg)

    return replace(quote, symbol=symbol, timestamp=timestamp)


def _validate_non_negative(field: str, value: Decimal) -> None:
    if value < 0:
        msg = f"Market data {field} must be non-negative"
        raise MarketDataValidationError(msg)

