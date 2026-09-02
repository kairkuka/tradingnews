import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config.assets import require_supported_symbol
from app.config.matching import (
    RELAXED_FALLBACK_THRESHOLD,
    RELAXED_PRIMARY_THRESHOLD,
    SIMILARITY_WEIGHTS,
    STRICT_THRESHOLD,
    HistoricalConfidence,
    MatchingMode,
    SimilarityWeights,
    confidence_from_sample_size,
)
from app.db.models import Event, MarketContext
from app.db.repositories.events import EventRepository
from app.db.repositories.market_context import MarketContextRepository


class HistoricalMatchingError(ValueError):
    """Raised when historical matching cannot be performed safely."""


@dataclass(frozen=True)
class SimilarityComponents:
    event_type_score: Decimal
    surprise_score: Decimal
    regime_score: Decimal
    volatility_score: Decimal
    dxy_score: Decimal
    yield_score: Decimal

    def weighted_total(self, weights: SimilarityWeights = SIMILARITY_WEIGHTS) -> Decimal:
        return (
            self.event_type_score * weights.event_type
            + self.surprise_score * weights.surprise
            + self.regime_score * weights.regime
            + self.volatility_score * weights.volatility
            + self.dxy_score * weights.dxy
            + self.yield_score * weights.yield_
        )


@dataclass(frozen=True)
class SimilarEventMatch:
    event: Event
    score: Decimal
    components: SimilarityComponents
    market_context: MarketContext | None


@dataclass(frozen=True)
class HistoricalMatchResult:
    current_event_id: uuid.UUID
    symbol: str
    mode: MatchingMode
    threshold: Decimal
    confidence: HistoricalConfidence
    low_confidence: bool
    candidate_count: int
    matches: tuple[SimilarEventMatch, ...]

    @property
    def sample_size(self) -> int:
        return len(self.matches)


class HistoricalMatcher:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.events = EventRepository(session)
        self.contexts = MarketContextRepository(session)

    def find_similar_events(
        self,
        current_event: Event,
        symbol: str,
        lookback_years: int = 10,
        min_samples: int = 20,
        mode: MatchingMode = MatchingMode.RELAXED,
    ) -> HistoricalMatchResult:
        current_event_id = _require_event_id(current_event)
        normalized_symbol = require_supported_symbol(symbol)
        if lookback_years < 1:
            msg = "lookback_years must be greater than zero"
            raise HistoricalMatchingError(msg)
        if min_samples < 1:
            msg = "min_samples must be greater than zero"
            raise HistoricalMatchingError(msg)

        current_timestamp = _normalize_timestamp(current_event.timestamp)
        since = current_timestamp - timedelta(days=365 * lookback_years)
        candidates = self.events.historical_candidates_with_reactions(
            event_type=current_event.event_type,
            before=current_timestamp,
            since=since,
            symbol=normalized_symbol,
        )
        current_context = self.contexts.get_for_event_symbol(current_event_id, normalized_symbol)
        scored = tuple(
            sorted(
                (
                    self._score_candidate(
                        current_event=current_event,
                        candidate=candidate,
                        symbol=normalized_symbol,
                        current_context=current_context,
                    )
                    for candidate in candidates
                ),
                key=lambda item: (item.score, _normalize_timestamp(item.event.timestamp)),
                reverse=True,
            )
        )

        threshold = STRICT_THRESHOLD if mode == MatchingMode.STRICT else RELAXED_PRIMARY_THRESHOLD
        matches = tuple(item for item in scored if item.score >= threshold)
        used_fallback = False
        if mode == MatchingMode.RELAXED and len(matches) < min_samples:
            threshold = RELAXED_FALLBACK_THRESHOLD
            matches = tuple(item for item in scored if item.score >= threshold)
            used_fallback = True

        confidence = confidence_from_sample_size(len(matches))
        return HistoricalMatchResult(
            current_event_id=current_event_id,
            symbol=normalized_symbol,
            mode=mode,
            threshold=threshold,
            confidence=confidence,
            low_confidence=used_fallback
            or confidence in (HistoricalConfidence.LOW, HistoricalConfidence.INSUFFICIENT)
            or len(matches) < min_samples,
            candidate_count=len(candidates),
            matches=matches,
        )

    def _score_candidate(
        self,
        *,
        current_event: Event,
        candidate: Event,
        symbol: str,
        current_context: MarketContext | None,
    ) -> SimilarEventMatch:
        candidate_context = self.contexts.get_for_event_symbol(_require_event_id(candidate), symbol)
        components = SimilarityComponents(
            event_type_score=_event_type_score(current_event, candidate),
            surprise_score=_surprise_score(current_event, candidate),
            regime_score=_categorical_score(
                _context_value(current_context, "trend"),
                _context_value(candidate_context, "trend"),
            ),
            volatility_score=_volatility_score(current_context, candidate_context),
            dxy_score=_numeric_score(
                _context_value(current_context, "dxy_change"),
                _context_value(candidate_context, "dxy_change"),
                scale=Decimal("1"),
            ),
            yield_score=_numeric_score(
                _context_value(current_context, "us10y_change"),
                _context_value(candidate_context, "us10y_change"),
                scale=Decimal("1"),
            ),
        )
        return SimilarEventMatch(
            event=candidate,
            score=components.weighted_total(),
            components=components,
            market_context=candidate_context,
        )


def find_similar_events(
    session: Session,
    current_event: Event,
    symbol: str,
    lookback_years: int = 10,
    min_samples: int = 20,
    mode: MatchingMode = MatchingMode.RELAXED,
) -> HistoricalMatchResult:
    return HistoricalMatcher(session).find_similar_events(
        current_event=current_event,
        symbol=symbol,
        lookback_years=lookback_years,
        min_samples=min_samples,
        mode=mode,
    )


def _event_type_score(current_event: Event, candidate: Event) -> Decimal:
    return Decimal("1") if current_event.event_type == candidate.event_type else Decimal("0")


def _surprise_score(current_event: Event, candidate: Event) -> Decimal:
    if current_event.surprise_zscore is not None and candidate.surprise_zscore is not None:
        return _numeric_score(
            current_event.surprise_zscore,
            candidate.surprise_zscore,
            scale=Decimal("3"),
        )
    if current_event.surprise_pct is not None and candidate.surprise_pct is not None:
        return _numeric_score(
            current_event.surprise_pct,
            candidate.surprise_pct,
            scale=Decimal("10"),
        )
    if current_event.surprise is not None and candidate.surprise is not None:
        scale = max(abs(current_event.surprise), abs(candidate.surprise), Decimal("1"))
        return _numeric_score(current_event.surprise, candidate.surprise, scale=scale)
    return Decimal("0.5")


def _volatility_score(
    current_context: MarketContext | None,
    candidate_context: MarketContext | None,
) -> Decimal:
    categorical = _categorical_score(
        _context_value(current_context, "volatility_regime"),
        _context_value(candidate_context, "volatility_regime"),
    )
    if categorical != Decimal("0.5"):
        return categorical
    return _numeric_score(
        _context_value(current_context, "atr_percentile"),
        _context_value(candidate_context, "atr_percentile"),
        scale=Decimal("100"),
    )


def _categorical_score(current_value: object, candidate_value: object) -> Decimal:
    if current_value is None or candidate_value is None:
        return Decimal("0.5")
    if str(current_value).lower() == str(candidate_value).lower():
        return Decimal("1")
    return Decimal("0")


def _numeric_score(
    current_value: object,
    candidate_value: object,
    *,
    scale: Decimal,
) -> Decimal:
    if current_value is None or candidate_value is None:
        return Decimal("0.5")
    current_decimal = Decimal(str(current_value))
    candidate_decimal = Decimal(str(candidate_value))
    if scale <= 0:
        msg = "Similarity score scale must be positive"
        raise HistoricalMatchingError(msg)
    score = Decimal("1") - (abs(current_decimal - candidate_decimal) / scale)
    return min(Decimal("1"), max(Decimal("0"), score))


def _context_value(context: MarketContext | None, attr: str) -> object:
    if context is None:
        return None
    return getattr(context, attr)


def _require_event_id(event: Event) -> uuid.UUID:
    if event.id is None:
        msg = "Event must have an id before historical matching"
        raise HistoricalMatchingError(msg)
    return event.id


def _normalize_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)
