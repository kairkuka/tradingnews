import uuid
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.config.assets import require_supported_symbol
from app.config.reactions import (
    DEFAULT_PRE_EVENT_WINDOW,
    HORIZON_DELTAS,
    REACTION_HORIZONS,
    SIGNIFICANT_MOVE_THRESHOLD_PCT,
    ReactionClassification,
    require_supported_horizon,
)
from app.db.models import Candle, Event
from app.db.repositories.candles import CandleRepository
from app.db.repositories.event_reactions import EventReactionRepository
from app.services.reaction_metrics import ReactionMetrics


class ReactionCalculationError(ValueError):
    """Raised when event reaction cannot be calculated from trusted market data."""


class ReactionEngine:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.candles = CandleRepository(session)
        self.reactions = EventReactionRepository(session)

    def calculate_for_event(
        self,
        event: Event,
        symbol: str,
        *,
        timeframe: str = "1m",
        horizons: Sequence[str] = REACTION_HORIZONS,
        pre_event_window: timedelta = DEFAULT_PRE_EVENT_WINDOW,
    ) -> tuple[ReactionMetrics, ...]:
        event_id = _event_id(event)
        normalized_symbol = require_supported_symbol(symbol)
        event_timestamp = normalize_reaction_timestamp(event.timestamp)
        price_before_candle = self.candles.last_before(
            normalized_symbol,
            timeframe,
            event_timestamp,
        )
        if price_before_candle is None:
            msg = "Cannot calculate reaction without a candle before event timestamp"
            raise ReactionCalculationError(msg)

        pre_event_start = event_timestamp - pre_event_window
        before_candles = self.candles.list_range(
            normalized_symbol,
            timeframe,
            pre_event_start,
            event_timestamp,
            include_start=True,
            include_end=False,
        )

        metrics = tuple(
            self._calculate_horizon(
                event_id=event_id,
                symbol=normalized_symbol,
                timeframe=timeframe,
                event_timestamp=event_timestamp,
                horizon=require_supported_horizon(horizon),
                price_before_candle=price_before_candle,
                before_candles=before_candles,
            )
            for horizon in horizons
        )
        classification = classify_reaction_path(metrics)
        return tuple(replace(item, classification=classification) for item in metrics)

    def calculate_and_store_for_event(
        self,
        event: Event,
        symbol: str,
        *,
        timeframe: str = "1m",
        horizons: Sequence[str] = REACTION_HORIZONS,
        commit: bool = True,
    ) -> tuple[ReactionMetrics, ...]:
        metrics = self.calculate_for_event(
            event,
            symbol,
            timeframe=timeframe,
            horizons=horizons,
        )
        for item in metrics:
            self.reactions.upsert(item)
        if commit:
            self.session.commit()
        return metrics

    def _calculate_horizon(
        self,
        *,
        event_id: uuid.UUID,
        symbol: str,
        timeframe: str,
        event_timestamp: datetime,
        horizon: str,
        price_before_candle: Candle,
        before_candles: Sequence[Candle],
    ) -> ReactionMetrics:
        horizon_end = event_timestamp + HORIZON_DELTAS[horizon]
        after_candles = self.candles.list_range(
            symbol,
            timeframe,
            event_timestamp,
            horizon_end,
            include_start=False,
            include_end=True,
        )
        if not after_candles:
            msg = f"Cannot calculate {horizon} reaction without candles after event timestamp"
            raise ReactionCalculationError(msg)

        price_before = price_before_candle.close
        price_after = after_candles[-1].close
        high_after = max(candle.high for candle in after_candles)
        low_after = min(candle.low for candle in after_candles)
        return_pct = calculate_return_pct(price_before, price_after)

        return ReactionMetrics(
            event_id=event_id,
            symbol=symbol,
            horizon=horizon,
            price_before=price_before,
            price_after=price_after,
            return_pct=return_pct,
            high_after=high_after,
            low_after=low_after,
            max_favorable_excursion=calculate_return_pct(price_before, high_after),
            max_adverse_excursion=calculate_return_pct(price_before, low_after),
            volatility_before=calculate_volatility(before_candles),
            volatility_after=calculate_volatility(after_candles),
            volume_before=sum_volume(before_candles),
            volume_after=sum_volume(after_candles),
            pre_event_return_pct=calculate_pre_event_return(before_candles, price_before),
            classification=ReactionClassification.NO_SIGNIFICANT_MOVE,
        )


def calculate_return_pct(price_before: Decimal, price_after: Decimal) -> Decimal:
    if price_before <= 0:
        msg = "price_before must be positive"
        raise ReactionCalculationError(msg)
    return ((price_after / price_before) - Decimal("1")) * Decimal("100")


def calculate_pre_event_return(
    before_candles: Sequence[Candle],
    price_before: Decimal,
) -> Decimal | None:
    if not before_candles:
        return None
    return calculate_return_pct(before_candles[0].close, price_before)


def calculate_volatility(candles: Sequence[Candle]) -> Decimal | None:
    if len(candles) < 2:
        return None

    returns = [
        calculate_return_pct(previous.close, current.close)
        for previous, current in zip(candles, candles[1:], strict=False)
    ]
    mean = sum(returns, Decimal("0")) / Decimal(len(returns))
    variance = sum((item - mean) ** 2 for item in returns) / Decimal(len(returns))

    try:
        return variance.sqrt()
    except InvalidOperation:
        return None


def sum_volume(candles: Sequence[Candle]) -> Decimal | None:
    values = [candle.volume for candle in candles if candle.volume is not None]
    if not values:
        return None
    return sum(values, Decimal("0"))


def classify_reaction_path(
    metrics: Sequence[ReactionMetrics],
    *,
    threshold_pct: Decimal = Decimal(str(SIGNIFICANT_MOVE_THRESHOLD_PCT)),
) -> ReactionClassification:
    significant = [item for item in metrics if abs(item.return_pct) >= threshold_pct]
    if not significant:
        return ReactionClassification.NO_SIGNIFICANT_MOVE

    first = significant[0]
    final = significant[-1]
    if _sign(first.return_pct) != _sign(final.return_pct):
        return ReactionClassification.REVERSAL

    if first.horizon not in ("1m", "5m"):
        return ReactionClassification.DELAYED

    if abs(final.return_pct) > abs(first.return_pct):
        return ReactionClassification.CONTINUATION

    return ReactionClassification.IMMEDIATE


def _event_id(event: Event) -> uuid.UUID:
    if event.id is None:
        msg = "Event must have an id before reaction calculation"
        raise ReactionCalculationError(msg)
    return event.id


def _sign(value: Decimal) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def normalize_reaction_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)
