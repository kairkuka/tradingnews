import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.models import Base, Event
from app.providers.economic.base import EconomicCalendarProvider
from app.providers.economic.schemas import EconomicCalendarEvent, EconomicCalendarValidationError
from app.services.economic_calendar import EconomicCalendarIngestionService
from app.services.event_normalizer import UnsupportedEconomicEventType


class StubEconomicCalendarProvider(EconomicCalendarProvider):
    def __init__(self, events: Sequence[EconomicCalendarEvent]) -> None:
        self.events = events

    async def get_upcoming_events(
        self,
        start: datetime,
        end: datetime,
        *,
        countries: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
    ) -> Sequence[EconomicCalendarEvent]:
        return self.events

    async def get_historical_events(
        self,
        start: datetime,
        end: datetime,
        *,
        countries: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
    ) -> Sequence[EconomicCalendarEvent]:
        return self.events

    async def get_event(self, provider_event_id: str) -> EconomicCalendarEvent:
        return self.events[0]


def test_economic_calendar_ingestion_stores_normalized_event() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event = EconomicCalendarEvent(
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        country="US",
        currency="USD",
        title="US CPI YoY",
        event_type="CPI",
        actual=Decimal("3.1"),
        forecast=Decimal("3.3"),
        previous=Decimal("3.4"),
        revision=Decimal("0.1"),
        unit="%",
        source="fixture",
    )

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        result = asyncio.run(
            service.ingest_historical_events(
                StubEconomicCalendarProvider([event]),
                datetime(2026, 9, 2, 12, 0, tzinfo=UTC),
                datetime(2026, 9, 2, 14, 0, tzinfo=UTC),
            )
        )

        stored = session.scalars(select(Event)).one()
        assert result.stored == 1
        assert result.skipped == 0
        assert stored.event_type == "US_CPI"
        assert stored.surprise == Decimal("-0.20000000")
        assert stored.surprise_zscore is None


def test_economic_calendar_ingestion_calculates_zscore_from_prior_events_only() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    events = (
        EconomicCalendarEvent(
            timestamp=datetime(2026, 1, 1, 13, 0, tzinfo=UTC),
            country="US",
            currency="USD",
            title="US CPI",
            event_type="CPI",
            actual=Decimal("2"),
            forecast=Decimal("1"),
        ),
        EconomicCalendarEvent(
            timestamp=datetime(2026, 2, 1, 13, 0, tzinfo=UTC),
            country="US",
            currency="USD",
            title="US CPI",
            event_type="CPI",
            actual=Decimal("5"),
            forecast=Decimal("2"),
        ),
        EconomicCalendarEvent(
            timestamp=datetime(2026, 3, 1, 13, 0, tzinfo=UTC),
            country="US",
            currency="USD",
            title="US CPI",
            event_type="CPI",
            actual=Decimal("7"),
            forecast=Decimal("3"),
        ),
    )

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        result = service.store_events(events)

        latest = session.scalars(select(Event).order_by(Event.timestamp.desc())).first()
        assert result.stored == 3
        assert latest is not None
        assert latest.surprise == Decimal("4.00000000")
        assert latest.surprise_zscore == Decimal("2.00000000")


def test_economic_calendar_ingestion_upserts_duplicate_event() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    timestamp = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)
    first = EconomicCalendarEvent(
        timestamp=timestamp,
        country="US",
        currency="USD",
        title="US CPI",
        event_type="CPI",
        actual=Decimal("3.1"),
        forecast=Decimal("3.3"),
        source="fixture",
    )
    second = EconomicCalendarEvent(
        timestamp=timestamp,
        country="US",
        currency="USD",
        title="US CPI",
        event_type="CPI",
        actual=Decimal("3.0"),
        forecast=Decimal("3.3"),
        source="fixture",
    )

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        service.store_events((first,))
        service.store_events((second,))

        stored = session.scalars(select(Event)).one()
        assert session.scalar(select(func.count()).select_from(Event)) == 1
        assert stored.surprise == Decimal("-0.30000000")


def test_economic_calendar_ingestion_skips_unsupported_by_default() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event = EconomicCalendarEvent(
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        country="US",
        currency="USD",
        title="Unsupported Event",
    )

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        result = service.store_events((event,))

        assert result.stored == 0
        assert result.skipped == 1


def test_economic_calendar_ingestion_can_raise_for_unsupported_events() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    event = EconomicCalendarEvent(
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        country="US",
        currency="USD",
        title="Unsupported Event",
    )

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        with pytest.raises(UnsupportedEconomicEventType):
            service.store_events((event,), skip_unsupported=False)


def test_economic_calendar_ingestion_rejects_invalid_window() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        service = EconomicCalendarIngestionService(session)
        with pytest.raises(EconomicCalendarValidationError, match="start timestamp"):
            asyncio.run(
                service.ingest_historical_events(
                    StubEconomicCalendarProvider(()),
                    datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
                    datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
                )
            )

