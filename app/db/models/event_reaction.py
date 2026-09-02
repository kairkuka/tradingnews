import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base
from app.db.models.types import MarketNumeric


class EventReaction(Base):
    __tablename__ = "event_reactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False, index=True)

    horizon: Mapped[str] = mapped_column(nullable=False, index=True)

    price_before: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    price_after: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)

    return_pct: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)

    high_after: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    low_after: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    max_favorable_excursion: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    max_adverse_excursion: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    volatility_before: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    volatility_after: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    volume_before: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    volume_after: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

