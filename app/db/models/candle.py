from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.types import BigIntPrimaryKey, MarketNumeric


class Candle(Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "timeframe",
            "timestamp",
            name="uq_candles_symbol_timeframe_timestamp",
        ),
        Index("ix_candles_symbol_timestamp", "symbol", "timestamp"),
        Index("ix_candles_symbol_timeframe_timestamp", "symbol", "timeframe", "timestamp"),
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True)

    symbol: Mapped[str] = mapped_column(nullable=False)
    timeframe: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    high: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    low: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    close: Mapped[Decimal] = mapped_column(MarketNumeric, nullable=False)
    volume: Mapped[Decimal | None] = mapped_column(MarketNumeric, nullable=True)
