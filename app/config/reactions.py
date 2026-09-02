from collections.abc import Mapping
from datetime import timedelta
from enum import StrEnum
from types import MappingProxyType


class ReactionClassification(StrEnum):
    IMMEDIATE = "IMMEDIATE"
    DELAYED = "DELAYED"
    REVERSAL = "REVERSAL"
    CONTINUATION = "CONTINUATION"
    NO_SIGNIFICANT_MOVE = "NO_SIGNIFICANT_MOVE"


class PriceReferenceMode(StrEnum):
    PREVIOUS_CLOSE = "previous_close"
    LAST_TICK = "last_tick"
    MID_PRICE = "mid_price"


REACTION_HORIZONS: tuple[str, ...] = ("1m", "5m", "15m", "30m", "1h", "2h", "4h", "1D")

HORIZON_DELTAS: Mapping[str, timedelta] = MappingProxyType(
    {
        "1m": timedelta(minutes=1),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "2h": timedelta(hours=2),
        "4h": timedelta(hours=4),
        "1D": timedelta(days=1),
    }
)

DEFAULT_PRE_EVENT_WINDOW = timedelta(minutes=30)
SIGNIFICANT_MOVE_THRESHOLD_PCT = 0.05


def require_supported_horizon(horizon: str) -> str:
    normalized = "1D" if horizon.strip().lower() == "1d" else horizon.strip()
    if normalized not in REACTION_HORIZONS:
        msg = f"Unsupported reaction horizon: {horizon}"
        raise ValueError(msg)
    return normalized

