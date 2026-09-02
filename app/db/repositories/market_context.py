import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MarketContext


class MarketContextRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_event_symbol(
        self,
        event_id: uuid.UUID,
        symbol: str,
    ) -> MarketContext | None:
        return self.session.scalars(
            select(MarketContext)
            .where(MarketContext.event_id == event_id, MarketContext.symbol == symbol)
            .order_by(MarketContext.timestamp.desc())
            .limit(1)
        ).first()

