from collections.abc import Mapping
from types import MappingProxyType

SUPPORTED_TIMEFRAMES: tuple[str, ...] = ("1m", "5m", "15m", "30m", "1h", "2h", "4h", "1D")

TIMEFRAME_SECONDS: Mapping[str, int] = MappingProxyType(
    {
        "1m": 60,
        "5m": 5 * 60,
        "15m": 15 * 60,
        "30m": 30 * 60,
        "1h": 60 * 60,
        "2h": 2 * 60 * 60,
        "4h": 4 * 60 * 60,
        "1D": 24 * 60 * 60,
    }
)


def normalize_timeframe(timeframe: str) -> str:
    value = timeframe.strip()
    return "1D" if value.lower() == "1d" else value


def require_supported_timeframe(timeframe: str) -> str:
    normalized = normalize_timeframe(timeframe)
    if normalized not in SUPPORTED_TIMEFRAMES:
        msg = f"Unsupported market data timeframe: {timeframe}"
        raise ValueError(msg)
    return normalized
