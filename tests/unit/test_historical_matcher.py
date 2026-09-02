from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.matching import HistoricalConfidence, MatchingMode
from app.db.models import Base, Event, EventReaction, MarketContext
from app.services.historical_matcher import HistoricalMatcher


def test_historical_matcher_returns_strict_same_type_matches() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        good = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("1.2"))
        bad = _event(session, current_time - timedelta(days=60), "US_CPI", Decimal("1.2"))
        _reaction(session, good.id, "XAUUSD")
        _reaction(session, bad.id, "XAUUSD")
        _context(session, current.id, current_time, "XAUUSD", "up", "high", "0.20", "0.10")
        _context(session, good.id, good.timestamp, "XAUUSD", "up", "high", "0.25", "0.10")
        _context(session, bad.id, bad.timestamp, "XAUUSD", "down", "low", "1.40", "-1.00")
        session.commit()

        result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=1,
            mode=MatchingMode.STRICT,
        )

        assert result.mode == MatchingMode.STRICT
        assert result.threshold == Decimal("0.80")
        assert result.candidate_count == 2
        assert result.sample_size == 1
        assert result.matches[0].event.id == good.id
        assert result.matches[0].score.quantize(Decimal("0.0001")) == Decimal("0.9750")


def test_historical_matcher_never_mixes_event_types_without_fallback() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        cpi = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("1.0"))
        nfp = _event(session, current_time - timedelta(days=31), "US_NFP", Decimal("1.0"))
        _reaction(session, cpi.id, "XAUUSD")
        _reaction(session, nfp.id, "XAUUSD")
        _context(session, current.id, current_time, "XAUUSD", "up", "high", "0.20", "0.10")
        _context(session, cpi.id, cpi.timestamp, "XAUUSD", "up", "high", "0.20", "0.10")
        session.commit()

        result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=1,
            mode=MatchingMode.STRICT,
        )

        assert result.candidate_count == 1
        assert result.matches[0].event.event_type == "US_CPI"


def test_historical_matcher_relaxed_mode_falls_back_to_060_when_samples_low() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        candidate = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("2.5"))
        _reaction(session, candidate.id, "XAUUSD")
        session.commit()

        result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=2,
            mode=MatchingMode.RELAXED,
        )

        assert result.threshold == Decimal("0.60")
        assert result.sample_size == 1
        assert result.low_confidence is True
        assert result.confidence == HistoricalConfidence.INSUFFICIENT


def test_historical_matcher_filters_by_lookback_and_symbol_reactions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    current_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        current = _event(session, current_time, "US_CPI", Decimal("1.0"))
        in_window = _event(session, current_time - timedelta(days=30), "US_CPI", Decimal("1.0"))
        too_old = _event(session, current_time - timedelta(days=800), "US_CPI", Decimal("1.0"))
        wrong_symbol = _event(session, current_time - timedelta(days=31), "US_CPI", Decimal("1.0"))
        _reaction(session, in_window.id, "XAUUSD")
        _reaction(session, too_old.id, "XAUUSD")
        _reaction(session, wrong_symbol.id, "EURUSD")
        _context(session, current.id, current_time, "XAUUSD", "up", "high", "0.20", "0.10")
        _context(
            session,
            in_window.id,
            in_window.timestamp,
            "XAUUSD",
            "up",
            "high",
            "0.20",
            "0.10",
        )
        session.commit()

        result = HistoricalMatcher(session).find_similar_events(
            current,
            "XAUUSD",
            lookback_years=1,
            min_samples=1,
            mode=MatchingMode.STRICT,
        )

        assert result.candidate_count == 1
        assert result.matches[0].event.id == in_window.id


def test_historical_matcher_rejects_unknown_symbol() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        current = _event(session, datetime(2026, 9, 2, 13, 0, tzinfo=UTC), "US_CPI", Decimal("1"))

        with pytest.raises(ValueError, match="Unsupported asset symbol"):
            HistoricalMatcher(session).find_similar_events(current, "AAPL")


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


def _reaction(session: Session, event_id: object, symbol: str) -> EventReaction:
    reaction = EventReaction(
        event_id=event_id,
        symbol=symbol,
        horizon="1m",
        price_before=Decimal("100"),
        price_after=Decimal("101"),
        return_pct=Decimal("1"),
    )
    session.add(reaction)
    session.flush()
    return reaction


def _context(
    session: Session,
    event_id: object,
    timestamp: datetime,
    symbol: str,
    trend: str,
    volatility_regime: str,
    dxy_change: str,
    us10y_change: str,
) -> MarketContext:
    context = MarketContext(
        id=uuid4(),
        event_id=event_id,
        symbol=symbol,
        timestamp=timestamp,
        trend=trend,
        volatility_regime=volatility_regime,
        dxy_change=Decimal(dxy_change),
        us10y_change=Decimal(us10y_change),
    )
    session.add(context)
    session.flush()
    return context
