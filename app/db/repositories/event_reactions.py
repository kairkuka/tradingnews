import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EventReaction
from app.services.reaction_metrics import ReactionMetrics


class EventReactionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, metrics: ReactionMetrics) -> EventReaction:
        existing = self.session.execute(
            select(EventReaction).where(
                EventReaction.event_id == metrics.event_id,
                EventReaction.symbol == metrics.symbol,
                EventReaction.horizon == metrics.horizon,
            )
        ).scalar_one_or_none()

        if existing is None:
            reaction = EventReaction(
                event_id=metrics.event_id,
                symbol=metrics.symbol,
                horizon=metrics.horizon,
                price_before=metrics.price_before,
                price_after=metrics.price_after,
                return_pct=metrics.return_pct,
                high_after=metrics.high_after,
                low_after=metrics.low_after,
                max_favorable_excursion=metrics.max_favorable_excursion,
                max_adverse_excursion=metrics.max_adverse_excursion,
                volatility_before=metrics.volatility_before,
                volatility_after=metrics.volatility_after,
                volume_before=metrics.volume_before,
                volume_after=metrics.volume_after,
            )
            self.session.add(reaction)
            return reaction

        existing.price_before = metrics.price_before
        existing.price_after = metrics.price_after
        existing.return_pct = metrics.return_pct
        existing.high_after = metrics.high_after
        existing.low_after = metrics.low_after
        existing.max_favorable_excursion = metrics.max_favorable_excursion
        existing.max_adverse_excursion = metrics.max_adverse_excursion
        existing.volatility_before = metrics.volatility_before
        existing.volatility_after = metrics.volatility_after
        existing.volume_before = metrics.volume_before
        existing.volume_after = metrics.volume_after
        return existing

    def list_for_event(self, event_id: uuid.UUID) -> tuple[EventReaction, ...]:
        rows = self.session.scalars(
            select(EventReaction)
            .where(EventReaction.event_id == event_id)
            .order_by(EventReaction.symbol, EventReaction.horizon)
        )
        return tuple(rows)
