import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base
from app.db.models.types import MarketNumeric


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    country: Mapped[str | None] = mapped_column(nullable=True)
    currency: Mapped[str | None] = mapped_column(nullable=True)

    category: Mapped[str] = mapped_column(nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)

    importance: Mapped[str | None] = mapped_column(nullable=True)

    actual: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    forecast: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    previous: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    revision: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    unit: Mapped[str | None] = mapped_column(nullable=True)

    surprise: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    surprise_pct: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    surprise_zscore: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    directionality: Mapped[str | None] = mapped_column(nullable=True)

    source: Mapped[str | None] = mapped_column(nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

