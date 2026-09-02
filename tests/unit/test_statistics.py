from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config.matching import HistoricalConfidence, MatchingMode
from app.db.models import Base, Event, EventReaction, HistoricalStatistic, MarketContext
from app.services.historical_matcher import HistoricalMatcher
from app.services.statistics import (
    StatisticsService,
    impact_score,
    impact_score_label,
    summarize_reactions,
)


def test_summarize_reactions_calculates_statistics() -> None:
    reactions = (
        _reaction_object(Decimal("-1.0"), Decimal("0.5"), Decimal("-1.5")),
        _reaction_object(Decimal("0.5"), Decimal("1.0"), Decimal("-0.5")),
        _reaction_object(Decimal("1.5"), Decimal("2.0"), Decimal("-0.2")),
        _reaction_object(Decimal("2.0"), Decimal("2.5"), Decimal("-0.1")),
    )

    summary = summarize_reactions(
        reactions,
        event_type="US_CPI",
        symbol="XAUUSD",
        horizon="1m",
    )

    assert summary.sample_size == 4
    assert summary.up_count == 3
    assert summary.down_count == 1
    assert summary.up_probability == Decimal("75.00")
    assert summary.down_probability == Decimal("25.00")
    assert summary.mean_return == Decimal("0.75")
    assert summary.median_return == Decimal("1.00")
    assert summary.std_return is not None
    assert summary.std_return.quantize(Decimal("0.0001")) == Decimal("1.1456")
    assert summary.p10 == Decimal("-0.55")
    assert summary.p25 == Decimal("0.125")
    assert summary.p50 == Decimal("1.00")
    assert summary.p75 == Decimal("1.625")
    assert summary.p90 == Decimal("1.85")
    assert summary.median_mfe == Decimal("1.50")
    assert summary.median_mae == Decimal("-0.35")
    assert summary.confidence == HistoricalConfidence.INSUFFICIENT
    assert summary.impact_score == Decimal("50.0000")
    assert summary.up_probability_ci is not None
    assert summary.median_return_ci is not None


def test_summarize_empty_reactions_marks_insufficient_without_fake_stats() -> None:
    summary = summarize_reactions((), event_type="US_CPI", symbol="XAUUSD", horizon="1m")

    assert summary.sample_size == 0
    assert summary.up_probability == Decimal("0")
    assert summary.down_probability == Decimal("0")
    assert summary.mean_return is None
    assert summary.median_return is None
    assert summary.confidence == HistoricalConfidence.INSUFFICIENT
    assert summary.impact_score == Decimal("0.00")


def test_impact_score_labels() -> None:
    assert impact_score_label(Decimal("85")) == "Strong historical bullish"
    assert impact_score_label(Decimal("45")) == "Moderate bullish"
    assert impact_score_label(Decimal("0")) == "Neutral / mixed"
    assert impact_score_label(Decimal("-45")) == "Moderate bearish"
    assert impact_score_label(Decimal("-85")) == "Strong historical bearish"


def test_impact_score_clamps_to_allowed_range() -> None:
    assert impact_score(Decimal("100"), Decimal("0"), Decimal("10")) == Decimal("100")
    assert impact_score(Decimal("0"), Decimal("100"), Decimal("-10")) == Decimal("-100")


def test_statistics_service_summarizes_and_stores_match_result() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        first = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("1.0"))
        second = _event(session, current_time - timedelta(days=60), "US_CPI", Decimal("1.2"))
        _context(session, current.id, current_time)
        _context(session, first.id, first.timestamp)
        _context(session, second.id, second.timestamp)
        _reaction(session, first.id, Decimal("1.0"))
        _reaction(session, second.id, Decimal("2.0"))
        session.commit()

        match_result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=1,
            mode=MatchingMode.STRICT,
        )
        summary = StatisticsService(session).summarize_and_store_matches(
            match_result,
            event_type="US_CPI",
            horizon="1m",
        )

        stored = session.scalars(select(HistoricalStatistic)).one()
        assert summary.sample_size == 2
        assert summary.up_probability == Decimal("100")
        assert stored.sample_size == 2
        assert stored.median_return == Decimal("1.50000000")
        assert stored.confidence == "INSUFFICIENT"


def test_statistics_service_upserts_existing_historical_statistic() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        first = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("1.0"))
        _context(session, current.id, current_time)
        _context(session, first.id, first.timestamp)
        _reaction(session, first.id, Decimal("1.0"))
        session.commit()

        match_result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=1,
            mode=MatchingMode.STRICT,
        )
        service = StatisticsService(session)
        service.summarize_and_store_matches(match_result, event_type="US_CPI", horizon="1m")
        service.summarize_and_store_matches(match_result, event_type="US_CPI", horizon="1m")

        assert session.scalar(select(func.count()).select_from(HistoricalStatistic)) == 1


def _reaction_object(
    return_pct: Decimal,
    mfe: Decimal,
    mae: Decimal,
) -> EventReaction:
    return EventReaction(
        event_id=uuid4(),
        symbol="XAUUSD",
        horizon="1m",
        price_before=Decimal("100"),
        price_after=Decimal("101"),
        return_pct=return_pct,
        max_favorable_excursion=mfe,
        max_adverse_excursion=mae,
    )


def _event(
    session: Session,
    timestamp: datetime,
    event_type: str,
    surprise_zscore: Decimal,
) -> Event:
    event = Event(
        id=uuid4(),
        timestamp=timestamp,
        country="US",
        currency="USD",
        category="inflation",
        event_type=event_type,
        title=event_type.replace("_", " "),
        surprise=surprise_zscore,
        surprise_zscore=surprise_zscore,
        directionality="HIGHER_IS_HAWKISH",
    )
    session.add(event)
    session.flush()
    return event


def _reaction(session: Session, event_id: object, return_pct: Decimal) -> EventReaction:
    reaction = EventReaction(
        event_id=event_id,
        symbol="XAUUSD",
        horizon="1m",
        price_before=Decimal("100"),
        price_after=Decimal("101"),
        return_pct=return_pct,
        max_favorable_excursion=return_pct + Decimal("0.5"),
        max_adverse_excursion=return_pct - Decimal("1.0"),
    )
    session.add(reaction)
    session.flush()
    return reaction


def _context(session: Session, event_id: object, timestamp: datetime) -> MarketContext:
    context = MarketContext(
        id=uuid4(),
        event_id=event_id,
        symbol="XAUUSD",
        timestamp=timestamp,
        trend="up",
        volatility_regime="high",
        dxy_change=Decimal("0.1"),
        us10y_change=Decimal("0.1"),
    )
    session.add(context)
    session.flush()
    return context

