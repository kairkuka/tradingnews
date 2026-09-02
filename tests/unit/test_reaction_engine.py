from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config.reactions import ReactionClassification
from app.db.models import Base, Event, EventReaction
from app.db.repositories.candles import CandleRepository
from app.providers.market.schemas import OhlcvBar
from app.services.reaction_engine import (
    ReactionCalculationError,
    ReactionEngine,
    calculate_return_pct,
)


def test_calculate_return_pct() -> None:
    assert calculate_return_pct(Decimal("100"), Decimal("101")) == Decimal("1.00")


def test_reaction_engine_calculates_horizon_metrics() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (
                _bar(event_time - timedelta(minutes=2), "99", "99.5", "98.5", "99", "10"),
                _bar(event_time - timedelta(minutes=1), "99", "100.5", "98.8", "100", "20"),
                _bar(event_time + timedelta(minutes=1), "100", "102", "99", "101", "5"),
                _bar(event_time + timedelta(minutes=2), "101", "103", "100", "102", "7"),
                _bar(event_time + timedelta(minutes=5), "102", "104", "101", "103", "9"),
            ),
        )

        metrics = ReactionEngine(session).calculate_for_event(
            event,
            "XAUUSD",
            horizons=("1m", "5m"),
        )

        one_minute = metrics[0]
        assert one_minute.horizon == "1m"
        assert one_minute.price_before == Decimal("100.00000000")
        assert one_minute.price_after == Decimal("101.00000000")
        assert one_minute.return_pct == Decimal("1.00")
        assert one_minute.high_after == Decimal("102.00000000")
        assert one_minute.low_after == Decimal("99.00000000")
        assert one_minute.max_favorable_excursion == Decimal("2.00")
        assert one_minute.max_adverse_excursion == Decimal("-1.00")
        assert one_minute.volume_before == Decimal("30.00000000")
        assert one_minute.volume_after == Decimal("5.00000000")
        assert one_minute.pre_event_return_pct.quantize(Decimal("0.00000001")) == Decimal(
            "1.01010101"
        )
        assert one_minute.classification == ReactionClassification.CONTINUATION

        five_minutes = metrics[1]
        assert five_minutes.return_pct == Decimal("3.00")
        assert five_minutes.volume_after == Decimal("21.00000000")
        assert five_minutes.classification == ReactionClassification.CONTINUATION


def test_reaction_engine_stores_and_upserts_reactions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (
                _bar(event_time - timedelta(minutes=1), "99", "101", "98", "100", "10"),
                _bar(event_time + timedelta(minutes=1), "100", "102", "99", "101", "5"),
            ),
        )

        service = ReactionEngine(session)
        service.calculate_and_store_for_event(event, "XAUUSD", horizons=("1m",))
        service.calculate_and_store_for_event(event, "XAUUSD", horizons=("1m",))

        stored = session.scalars(select(EventReaction)).one()
        assert session.scalar(select(func.count()).select_from(EventReaction)) == 1
        assert stored.return_pct == Decimal("1.00000000")


def test_reaction_engine_rejects_missing_price_before() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        event = _store_event(session, datetime(2026, 9, 2, 13, 0, tzinfo=UTC))

        with pytest.raises(ReactionCalculationError, match="before event timestamp"):
            ReactionEngine(session).calculate_for_event(event, "XAUUSD", horizons=("1m",))


def test_reaction_engine_rejects_missing_after_window() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (_bar(event_time - timedelta(minutes=1), "99", "101", "98", "100", "10"),),
        )

        with pytest.raises(ReactionCalculationError, match="after event timestamp"):
            ReactionEngine(session).calculate_for_event(event, "XAUUSD", horizons=("1m",))


def test_reaction_engine_classifies_no_significant_move() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (
                _bar(event_time - timedelta(minutes=1), "100", "100", "100", "100", "10"),
                _bar(event_time + timedelta(minutes=1), "100", "100.02", "99.98", "100.01", "5"),
            ),
        )

        metrics = ReactionEngine(session).calculate_for_event(event, "XAUUSD", horizons=("1m",))

        assert metrics[0].classification == ReactionClassification.NO_SIGNIFICANT_MOVE


def test_reaction_engine_classifies_reversal() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (
                _bar(event_time - timedelta(minutes=1), "99", "101", "98", "100", "10"),
                _bar(event_time + timedelta(minutes=1), "100", "102", "99", "101", "5"),
                _bar(event_time + timedelta(minutes=5), "101", "101.5", "98", "99", "9"),
            ),
        )

        metrics = ReactionEngine(session).calculate_for_event(
            event,
            "XAUUSD",
            horizons=("1m", "5m"),
        )

        assert metrics[0].classification == ReactionClassification.REVERSAL
        assert metrics[1].classification == ReactionClassification.REVERSAL


def test_reaction_engine_classifies_delayed() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event_time = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)

    with Session(engine) as session:
        event = _store_event(session, event_time)
        _store_candles(
            session,
            (
                _bar(event_time - timedelta(minutes=1), "99", "101", "98", "100", "10"),
                _bar(event_time + timedelta(minutes=1), "100", "100.02", "99.99", "100.01", "5"),
                _bar(event_time + timedelta(minutes=15), "100", "101", "99", "100.1", "9"),
            ),
        )

        metrics = ReactionEngine(session).calculate_for_event(
            event,
            "XAUUSD",
            horizons=("1m", "15m"),
        )

        assert metrics[0].classification == ReactionClassification.DELAYED
        assert metrics[1].classification == ReactionClassification.DELAYED


def _store_event(session: Session, timestamp: datetime) -> Event:
    event = Event(
        id=uuid4(),
        timestamp=timestamp,
        country="US",
        currency="USD",
        category="inflation",
        event_type="US_CPI",
        title="US CPI",
    )
    session.add(event)
    session.flush()
    return event


def _store_candles(session: Session, bars: tuple[OhlcvBar, ...]) -> None:
    repo = CandleRepository(session)
    repo.upsert_many(bars)
    session.flush()


def _bar(
    timestamp: datetime,
    open_: str,
    high: str,
    low: str,
    close: str,
    volume: str,
) -> OhlcvBar:
    return OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=timestamp,
        open=Decimal(open_),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal(volume),
    )
