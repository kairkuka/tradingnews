from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.providers.economic.schemas import EconomicCalendarEvent
from app.services.event_normalizer import EventNormalizer, UnsupportedEconomicEventType


def test_event_normalizer_creates_canonical_event_with_surprise() -> None:
    source_timestamp = datetime(2026, 9, 2, 18, 0, tzinfo=timezone(timedelta(hours=5)))
    event = EconomicCalendarEvent(
        timestamp=source_timestamp,
        country="United States",
        currency="usd",
        title="US CPI YoY",
        event_type="CPI",
        importance="high",
        actual=Decimal("3.1"),
        forecast=Decimal("3.3"),
        previous=Decimal("3.4"),
        revision=Decimal("0.1"),
        unit="%",
        source="fixture",
        source_url="https://example.test/cpi",
    )

    normalized = EventNormalizer().normalize(event)

    assert normalized.timestamp == datetime(2026, 9, 2, 13, 0, tzinfo=UTC)
    assert normalized.country == "US"
    assert normalized.currency == "USD"
    assert normalized.category == "inflation"
    assert normalized.event_type == "US_CPI"
    assert normalized.actual == Decimal("3.1")
    assert normalized.forecast == Decimal("3.3")
    assert normalized.previous == Decimal("3.4")
    assert normalized.revision == Decimal("0.1")
    assert normalized.surprise == Decimal("-0.2")
    assert normalized.surprise_pct == Decimal("-6.060606060606060606060606061")
    assert normalized.directionality == "HIGHER_IS_HAWKISH"


def test_event_normalizer_rejects_unsupported_event() -> None:
    event = EconomicCalendarEvent(
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        country="US",
        currency="USD",
        title="Unsupported Event",
    )

    with pytest.raises(UnsupportedEconomicEventType, match="Unsupported economic event type"):
        EventNormalizer().normalize(event)

