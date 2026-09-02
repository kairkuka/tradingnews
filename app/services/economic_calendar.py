from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.repositories import EventRepository
from app.providers.economic.base import EconomicCalendarProvider
from app.providers.economic.schemas import (
    EconomicCalendarEvent,
    EconomicCalendarValidationError,
    ensure_utc_timestamp,
)
from app.services.event_normalizer import EventNormalizer, UnsupportedEconomicEventType
from app.services.surprise import calculate_zscore


@dataclass(frozen=True)
class EconomicCalendarIngestionResult:
    stored: int
    skipped: int


class EconomicCalendarIngestionService:
    def __init__(
        self,
        session: Session,
        normalizer: EventNormalizer | None = None,
    ) -> None:
        self.session = session
        self.events = EventRepository(session)
        self.normalizer = normalizer or EventNormalizer()

    async def ingest_upcoming_events(
        self,
        provider: EconomicCalendarProvider,
        start: datetime,
        end: datetime,
        *,
        countries: tuple[str, ...] | None = None,
        event_types: tuple[str, ...] | None = None,
        commit: bool = True,
    ) -> EconomicCalendarIngestionResult:
        utc_start, utc_end = _validate_window(start, end)
        events = await provider.get_upcoming_events(
            utc_start,
            utc_end,
            countries=countries,
            event_types=event_types,
        )
        return self.store_events(events, commit=commit)

    async def ingest_historical_events(
        self,
        provider: EconomicCalendarProvider,
        start: datetime,
        end: datetime,
        *,
        countries: tuple[str, ...] | None = None,
        event_types: tuple[str, ...] | None = None,
        commit: bool = True,
    ) -> EconomicCalendarIngestionResult:
        utc_start, utc_end = _validate_window(start, end)
        events = await provider.get_historical_events(
            utc_start,
            utc_end,
            countries=countries,
            event_types=event_types,
        )
        return self.store_events(events, commit=commit)

    def store_events(
        self,
        events: Sequence[EconomicCalendarEvent],
        *,
        skip_unsupported: bool = True,
        commit: bool = True,
    ) -> EconomicCalendarIngestionResult:
        stored = 0
        skipped = 0

        for event in sorted(events, key=lambda item: item.timestamp):
            try:
                normalized = self.normalizer.normalize(event)
            except UnsupportedEconomicEventType:
                if not skip_unsupported:
                    raise
                skipped += 1
                continue

            historical_surprises = self.events.historical_surprises_before(
                normalized.event_type,
                normalized.timestamp,
            )
            normalized = replace(
                normalized,
                surprise_zscore=calculate_zscore(normalized.surprise, historical_surprises),
            )
            self.events.upsert(normalized)
            stored += 1

        if commit:
            self.session.commit()

        return EconomicCalendarIngestionResult(stored=stored, skipped=skipped)


def _validate_window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    utc_start = ensure_utc_timestamp(start)
    utc_end = ensure_utc_timestamp(end)
    if utc_start >= utc_end:
        msg = "Economic calendar start timestamp must be before end timestamp"
        raise EconomicCalendarValidationError(msg)
    return utc_start, utc_end
