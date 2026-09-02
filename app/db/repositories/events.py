from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Event, EventReaction
from app.services.event_normalizer import NormalizedEconomicEvent


class EventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, normalized: NormalizedEconomicEvent) -> Event:
        existing = self.session.execute(
            select(Event).where(
                Event.timestamp == normalized.timestamp,
                Event.country == normalized.country,
                Event.currency == normalized.currency,
                Event.event_type == normalized.event_type,
                Event.title == normalized.title,
                Event.source == normalized.source,
            )
        ).scalar_one_or_none()

        if existing is None:
            event = Event(
                timestamp=normalized.timestamp,
                country=normalized.country,
                currency=normalized.currency,
                category=normalized.category,
                event_type=normalized.event_type,
                title=normalized.title,
                importance=normalized.importance,
                actual=normalized.actual,
                forecast=normalized.forecast,
                previous=normalized.previous,
                revision=normalized.revision,
                unit=normalized.unit,
                surprise=normalized.surprise,
                surprise_pct=normalized.surprise_pct,
                surprise_zscore=normalized.surprise_zscore,
                directionality=normalized.directionality,
                source=normalized.source,
                source_url=normalized.source_url,
            )
            self.session.add(event)
            return event

        existing.category = normalized.category
        existing.importance = normalized.importance
        existing.actual = normalized.actual
        existing.forecast = normalized.forecast
        existing.previous = normalized.previous
        existing.revision = normalized.revision
        existing.unit = normalized.unit
        existing.surprise = normalized.surprise
        existing.surprise_pct = normalized.surprise_pct
        existing.surprise_zscore = normalized.surprise_zscore
        existing.directionality = normalized.directionality
        existing.source_url = normalized.source_url
        return existing

    def historical_surprises_before(
        self,
        event_type: str,
        before: datetime,
    ) -> tuple[Decimal, ...]:
        rows = self.session.scalars(
            select(Event.surprise)
            .where(
                Event.event_type == event_type,
                Event.timestamp < before,
                Event.surprise.is_not(None),
            )
            .order_by(Event.timestamp)
        )
        return tuple(item for item in rows if item is not None)

    def historical_candidates_with_reactions(
        self,
        *,
        event_type: str,
        before: datetime,
        since: datetime,
        symbol: str,
    ) -> tuple[Event, ...]:
        has_reaction_for_symbol = (
            select(EventReaction.id)
            .where(
                EventReaction.event_id == Event.id,
                EventReaction.symbol == symbol,
            )
            .exists()
        )
        rows = self.session.scalars(
            select(Event)
            .where(
                Event.event_type == event_type,
                Event.timestamp < before,
                Event.timestamp >= since,
                has_reaction_for_symbol,
            )
            .order_by(Event.timestamp.desc())
        )
        return tuple(rows)
