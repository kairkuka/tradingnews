import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base
from app.db.models.types import MarketNumeric


class News(Base):
    __tablename__ = "news"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    source: Mapped[str] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

    country: Mapped[str | None] = mapped_column(nullable=True)
    language: Mapped[str | None] = mapped_column(nullable=True)

    event_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id"),
        nullable=True,
        index=True,
    )

    category: Mapped[str | None] = mapped_column(nullable=True, index=True)
    importance: Mapped[str | None] = mapped_column(nullable=True)

    sentiment: Mapped[str | None] = mapped_column(nullable=True)
    sentiment_score: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    embedding: Mapped[list[float] | dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

