from collections.abc import Sequence
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.config.matching import confidence_from_sample_size
from app.db.models import EventReaction
from app.db.repositories.event_reactions import EventReactionRepository
from app.db.repositories.historical_statistics import HistoricalStatisticsRepository
from app.services.bootstrap import bootstrap_confidence_interval, percentile
from app.services.historical_matcher import HistoricalMatchResult
from app.services.statistics_schemas import StatisticsSummary

IMPACT_MEDIAN_WEIGHT = Decimal("10")
IMPACT_SKEW_WEIGHT = Decimal("0.80")
IMPACT_MEDIAN_CAP = Decimal("20")


class StatisticsCalculationError(ValueError):
    """Raised when statistics input is inconsistent."""


class StatisticsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.reactions = EventReactionRepository(session)
        self.historical_statistics = HistoricalStatisticsRepository(session)

    def summarize_matches(
        self,
        match_result: HistoricalMatchResult,
        *,
        event_type: str,
        horizon: str,
    ) -> StatisticsSummary:
        event_ids = tuple(match.event.id for match in match_result.matches)
        reactions = self.reactions.list_for_events(
            event_ids,
            symbol=match_result.symbol,
            horizon=horizon,
        )
        return summarize_reactions(
            reactions,
            event_type=event_type,
            symbol=match_result.symbol,
            horizon=horizon,
        )

    def summarize_and_store_matches(
        self,
        match_result: HistoricalMatchResult,
        *,
        event_type: str,
        horizon: str,
        commit: bool = True,
    ) -> StatisticsSummary:
        summary = self.summarize_matches(
            match_result,
            event_type=event_type,
            horizon=horizon,
        )
        self.historical_statistics.upsert(summary)
        if commit:
            self.session.commit()
        return summary


def summarize_reactions(
    reactions: Sequence[EventReaction],
    *,
    event_type: str,
    symbol: str,
    horizon: str,
) -> StatisticsSummary:
    returns = tuple(reaction.return_pct for reaction in reactions)
    mfes = tuple(
        reaction.max_favorable_excursion
        for reaction in reactions
        if reaction.max_favorable_excursion is not None
    )
    maes = tuple(
        reaction.max_adverse_excursion
        for reaction in reactions
        if reaction.max_adverse_excursion is not None
    )
    sample_size = len(returns)
    up_count = sum(1 for item in returns if item > 0)
    down_count = sum(1 for item in returns if item < 0)
    up_probability = percentage(up_count, sample_size)
    down_probability = percentage(down_count, sample_size)
    median_return = median(returns)

    return StatisticsSummary(
        event_type=event_type,
        symbol=symbol,
        horizon=horizon,
        sample_size=sample_size,
        up_count=up_count,
        down_count=down_count,
        up_probability=up_probability,
        down_probability=down_probability,
        mean_return=mean(returns),
        median_return=median_return,
        std_return=stddev(returns),
        p10=percentile(returns, Decimal("0.10")),
        p25=percentile(returns, Decimal("0.25")),
        p50=percentile(returns, Decimal("0.50")),
        p75=percentile(returns, Decimal("0.75")),
        p90=percentile(returns, Decimal("0.90")),
        median_mfe=median(mfes),
        median_mae=median(maes),
        up_probability_ci=bootstrap_confidence_interval(returns, up_probability_statistic),
        median_return_ci=bootstrap_confidence_interval(returns, median),
        confidence=confidence_from_sample_size(sample_size),
        impact_score=impact_score(up_probability, down_probability, median_return),
    )


def mean(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def median(values: Sequence[Decimal]) -> Decimal | None:
    return percentile(values, Decimal("0.50"))


def stddev(values: Sequence[Decimal]) -> Decimal | None:
    if len(values) < 2:
        return None
    values_mean = mean(values)
    if values_mean is None:
        return None
    variance = sum((item - values_mean) ** 2 for item in values) / Decimal(len(values))
    try:
        return variance.sqrt()
    except InvalidOperation:
        return None


def percentage(numerator: int, denominator: int) -> Decimal:
    if denominator == 0:
        return Decimal("0")
    return (Decimal(numerator) / Decimal(denominator)) * Decimal("100")


def up_probability_statistic(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return percentage(sum(1 for item in values if item > 0), len(values))


def impact_score(
    up_probability: Decimal,
    down_probability: Decimal,
    median_return: Decimal | None,
) -> Decimal:
    skew_component = (up_probability - down_probability) * IMPACT_SKEW_WEIGHT
    median_component = Decimal("0")
    if median_return is not None:
        median_component = _clamp(
            median_return * IMPACT_MEDIAN_WEIGHT,
            -IMPACT_MEDIAN_CAP,
            IMPACT_MEDIAN_CAP,
        )
    return _clamp(skew_component + median_component, Decimal("-100"), Decimal("100"))


def impact_score_label(score: Decimal) -> str:
    if score >= 80:
        return "Strong historical bullish"
    if score >= 40:
        return "Moderate bullish"
    if score <= -80:
        return "Strong historical bearish"
    if score <= -40:
        return "Moderate bearish"
    return "Neutral / mixed"


def _clamp(value: Decimal, lower: Decimal, upper: Decimal) -> Decimal:
    return min(upper, max(lower, value))

