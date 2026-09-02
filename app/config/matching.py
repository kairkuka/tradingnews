from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType


class MatchingMode(StrEnum):
    STRICT = "STRICT"
    RELAXED = "RELAXED"


class HistoricalConfidence(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class SimilarityWeights:
    event_type: Decimal = Decimal("0.25")
    surprise: Decimal = Decimal("0.30")
    regime: Decimal = Decimal("0.15")
    volatility: Decimal = Decimal("0.10")
    dxy: Decimal = Decimal("0.10")
    yield_: Decimal = Decimal("0.10")


SIMILARITY_WEIGHTS = SimilarityWeights()
STRICT_THRESHOLD = Decimal("0.80")
RELAXED_PRIMARY_THRESHOLD = Decimal("0.70")
RELAXED_FALLBACK_THRESHOLD = Decimal("0.60")

CONFIDENCE_THRESHOLDS: Mapping[HistoricalConfidence, int] = MappingProxyType(
    {
        HistoricalConfidence.HIGH: 50,
        HistoricalConfidence.MEDIUM: 30,
        HistoricalConfidence.LOW: 15,
    }
)


def confidence_from_sample_size(sample_size: int) -> HistoricalConfidence:
    if sample_size >= CONFIDENCE_THRESHOLDS[HistoricalConfidence.HIGH]:
        return HistoricalConfidence.HIGH
    if sample_size >= CONFIDENCE_THRESHOLDS[HistoricalConfidence.MEDIUM]:
        return HistoricalConfidence.MEDIUM
    if sample_size >= CONFIDENCE_THRESHOLDS[HistoricalConfidence.LOW]:
        return HistoricalConfidence.LOW
    return HistoricalConfidence.INSUFFICIENT

