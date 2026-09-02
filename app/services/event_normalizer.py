from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.config.event_types import (
    canonical_event_type,
    get_directionality,
    normalize_country,
    resolve_event_type,
)
from app.providers.economic.schemas import EconomicCalendarEvent, validate_economic_calendar_event
from app.services.surprise import calculate_surprise, calculate_surprise_pct


class UnsupportedEconomicEventType(ValueError):
    """Raised when an event is outside the configured MVP event registry."""


@dataclass(frozen=True)
class NormalizedEconomicEvent:
    timestamp: datetime
    country: str
    currency: str
    category: str
    event_type: str
    title: str
    importance: str | None
    actual: Decimal | None
    forecast: Decimal | None
    previous: Decimal | None
    revision: Decimal | None
    unit: str | None
    surprise: Decimal | None
    surprise_pct: Decimal | None
    surprise_zscore: Decimal | None
    directionality: str
    source: str | None
    source_url: str | None


class EventNormalizer:
    def normalize(self, event: EconomicCalendarEvent) -> NormalizedEconomicEvent:
        validated = validate_economic_calendar_event(event)
        label = validated.event_type or validated.title
        config = resolve_event_type(label)
        if config is None:
            msg = f"Unsupported economic event type: {label}"
            raise UnsupportedEconomicEventType(msg)

        country = normalize_country(validated.country)
        event_type = canonical_event_type(country, config.canonical_type)
        directionality = get_directionality(country, config.canonical_type)
        surprise = calculate_surprise(validated.actual, validated.forecast)

        return NormalizedEconomicEvent(
            timestamp=validated.timestamp,
            country=country,
            currency=validated.currency,
            category=config.category.value,
            event_type=event_type,
            title=validated.title,
            importance=validated.importance,
            actual=validated.actual,
            forecast=validated.forecast,
            previous=validated.previous,
            revision=validated.revision,
            unit=validated.unit,
            surprise=surprise,
            surprise_pct=calculate_surprise_pct(surprise, validated.forecast),
            surprise_zscore=None,
            directionality=directionality.value,
            source=validated.source,
            source_url=validated.source_url,
        )

