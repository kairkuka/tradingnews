import uuid
from dataclasses import dataclass
from decimal import Decimal

from app.config.reactions import ReactionClassification


@dataclass(frozen=True)
class ReactionMetrics:
    event_id: uuid.UUID
    symbol: str
    horizon: str
    price_before: Decimal
    price_after: Decimal
    return_pct: Decimal
    high_after: Decimal | None
    low_after: Decimal | None
    max_favorable_excursion: Decimal | None
    max_adverse_excursion: Decimal | None
    volatility_before: Decimal | None
    volatility_after: Decimal | None
    volume_before: Decimal | None
    volume_after: Decimal | None
    pre_event_return_pct: Decimal | None
    classification: ReactionClassification

