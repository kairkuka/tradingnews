import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base
from app.db.models.types import MarketNumeric


class MarketContext(Base):
    __tablename__ = "market_context"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(nullable=False, index=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    trend: Mapped[str | None] = mapped_column(nullable=True)

    atr: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    atr_percentile: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    rsi: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    dxy_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    us10y_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    vix: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    gold_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    silver_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    gold_silver_ratio: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    oil_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    btc_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    nq_change: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

    session: Mapped[str | None] = mapped_column(nullable=True)

    volatility_regime: Mapped[str | None] = mapped_column(nullable=True)

    distance_from_daily_high: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
    distance_from_daily_low: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)

