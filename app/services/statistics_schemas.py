from dataclasses import dataclass
from decimal import Decimal

from app.config.matching import HistoricalConfidence


@dataclass(frozen=True)
class BootstrapInterval:
    lower: Decimal
    upper: Decimal


@dataclass(frozen=True)
class StatisticsSummary:
    event_type: str
    symbol: str
    horizon: str
    sample_size: int
    up_count: int
    down_count: int
    up_probability: Decimal
    down_probability: Decimal
    mean_return: Decimal | None
    median_return: Decimal | None
    std_return: Decimal | None
    p10: Decimal | None
    p25: Decimal | None
    p50: Decimal | None
    p75: Decimal | None
    p90: Decimal | None
    median_mfe: Decimal | None
    median_mae: Decimal | None
    up_probability_ci: BootstrapInterval | None
    median_return_ci: BootstrapInterval | None
    confidence: HistoricalConfidence
    impact_score: Decimal

