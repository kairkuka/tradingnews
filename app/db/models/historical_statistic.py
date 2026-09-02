import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base
from app.db.models.types import MarketNumeric


class HistoricalStatistic(Base):
    __tablename__ = "historical_statistics"
    __table_args__ = (
        UniqueConstraint(
            "event_type",
            "symbol",
            "horizon",
            name="uq_historical_statistics_event_symbol_horizon",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_type: Mapped[str] = mapped_column(nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(nullable=False, index=True)

    sample_size: Mapped[int] = mapped_column(nullable=False)

    up_count: Mapped[int] = mapped_column(nullable=False)
    down_count: Mapped[int] = mapped_column(nullable=False)

    up_probability: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    down_probability: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)

    mean_return: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    median_return: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    std_return: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    p10: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    p25: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    p50: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    p75: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    p90: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    median_mfe: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    median_mae: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    confidence: Mapped[str] = mapped_column(nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

