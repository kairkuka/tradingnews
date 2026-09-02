from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal


class EconomicCalendarValidationError(ValueError):
    """Raised when economic calendar data cannot be trusted for ingestion."""


@dataclass(frozen=True)
class EconomicCalendarEvent:
    timestamp: datetime
    country: str
    currency: str
    title: str
    provider_event_id: str | None = None
    event_type: str | None = None
    importance: str | None = None
    actual: Decimal | None = None
    forecast: Decimal | None = None
    previous: Decimal | None = None
    revision: Decimal | None = None
    unit: str | None = None
    source: str | None = None
    source_url: str | None = None


def ensure_utc_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        msg = "Economic calendar timestamp must be timezone-aware UTC"
        raise EconomicCalendarValidationError(msg)
    return timestamp.astimezone(UTC)


def validate_economic_calendar_event(event: EconomicCalendarEvent) -> EconomicCalendarEvent:
    timestamp = ensure_utc_timestamp(event.timestamp)
    country = event.country.strip()
    currency = event.currency.strip().upper()
    title = event.title.strip()

    if not country:
        msg = "Economic calendar country is required"
        raise EconomicCalendarValidationError(msg)
    if not currency:
        msg = "Economic calendar currency is required"
        raise EconomicCalendarValidationError(msg)
    if not title:
        msg = "Economic calendar title is required"
        raise EconomicCalendarValidationError(msg)

    return replace(event, timestamp=timestamp, country=country, currency=currency, title=title)

