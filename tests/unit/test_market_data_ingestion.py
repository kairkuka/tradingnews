import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.models import Asset, Base, Candle
from app.providers.market.base import MarketDataProvider
from app.providers.market.schemas import MarketDataValidationError, OhlcvBar, Quote
from app.services.market_data import MarketDataIngestionService


class StubMarketDataProvider(MarketDataProvider):
    def __init__(self, bars: Sequence[OhlcvBar]) -> None:
        self.bars = bars

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[OhlcvBar]:
        return self.bars

    async def get_latest_price(self, symbol: str) -> Decimal:
        return Decimal("2500")

    async def get_quote(self, symbol: str) -> Quote:
        return Quote(
            symbol=symbol,
            timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
            bid=Decimal("2499"),
            ask=Decimal("2501"),
            last=Decimal("2500"),
        )


def test_market_data_ingestion_stores_assets_and_candles() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    bar = OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        open=Decimal("2500"),
        high=Decimal("2510"),
        low=Decimal("2490"),
        close=Decimal("2505"),
        volume=Decimal("100"),
    )

    with Session(engine) as session:
        service = MarketDataIngestionService(session)
        count = asyncio.run(
            service.ingest_ohlcv(
                StubMarketDataProvider([bar]),
                "XAUUSD",
                "1m",
                datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
                datetime(2026, 9, 2, 13, 1, tzinfo=UTC),
            )
        )

        assert count == 1
        assert session.scalar(select(func.count()).select_from(Asset)) == 13
        assert session.scalar(select(func.count()).select_from(Candle)) == 1


def test_market_data_ingestion_upserts_duplicate_candles() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    timestamp = datetime(2026, 9, 2, 13, 0, tzinfo=UTC)
    first = OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=timestamp,
        open=Decimal("2500"),
        high=Decimal("2510"),
        low=Decimal("2490"),
        close=Decimal("2505"),
        volume=Decimal("100"),
    )
    second = OhlcvBar(
        symbol="XAUUSD",
        timeframe="1m",
        timestamp=timestamp,
        open=Decimal("2500"),
        high=Decimal("2512"),
        low=Decimal("2490"),
        close=Decimal("2508"),
        volume=Decimal("110"),
    )

    with Session(engine) as session:
        service = MarketDataIngestionService(session)
        service.store_ohlcv_bars([first])
        service.store_ohlcv_bars([second])

        candle = session.scalars(select(Candle)).one()
        assert session.scalar(select(func.count()).select_from(Candle)) == 1
        assert candle.close == Decimal("2508.00000000")
        assert candle.volume == Decimal("110.00000000")


def test_market_data_ingestion_rejects_provider_symbol_mismatch() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    bar = OhlcvBar(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 9, 2, 13, 0, tzinfo=UTC),
        open=Decimal("1.1000"),
        high=Decimal("1.1010"),
        low=Decimal("1.0990"),
        close=Decimal("1.1005"),
        volume=None,
    )

    with Session(engine) as session:
        service = MarketDataIngestionService(session)
        with pytest.raises(MarketDataValidationError, match="different symbol"):
            service.store_ohlcv_bars([bar], requested_symbol="XAUUSD")

