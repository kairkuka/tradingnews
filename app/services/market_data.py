from collections.abc import Iterable
from datetime import datetime

from sqlalchemy.orm import Session

from app.config.assets import require_supported_symbol
from app.config.market_data import require_supported_timeframe
from app.db.repositories import AssetRepository, CandleRepository
from app.providers.market.base import MarketDataProvider
from app.providers.market.schemas import (
    MarketDataValidationError,
    OhlcvBar,
    ensure_utc_timestamp,
    validate_ohlcv_bar,
)


class MarketDataIngestionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.assets = AssetRepository(session)
        self.candles = CandleRepository(session)

    async def ingest_ohlcv(
        self,
        provider: MarketDataProvider,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        *,
        commit: bool = True,
    ) -> int:
        requested_symbol = require_supported_symbol(symbol)
        requested_timeframe = require_supported_timeframe(timeframe)
        utc_start = ensure_utc_timestamp(start)
        utc_end = ensure_utc_timestamp(end)
        if utc_start >= utc_end:
            msg = "OHLCV start timestamp must be before end timestamp"
            raise MarketDataValidationError(msg)

        bars = await provider.get_ohlcv(
            requested_symbol,
            requested_timeframe,
            utc_start,
            utc_end,
        )
        return self.store_ohlcv_bars(
            bars,
            requested_symbol=requested_symbol,
            requested_timeframe=requested_timeframe,
            commit=commit,
        )

    def store_ohlcv_bars(
        self,
        bars: Iterable[OhlcvBar],
        *,
        requested_symbol: str | None = None,
        requested_timeframe: str | None = None,
        commit: bool = True,
    ) -> int:
        normalized_symbol = (
            require_supported_symbol(requested_symbol) if requested_symbol is not None else None
        )
        normalized_timeframe = (
            require_supported_timeframe(requested_timeframe)
            if requested_timeframe is not None
            else None
        )

        self.assets.upsert_supported_assets()
        validated_bars: list[OhlcvBar] = []
        for bar in bars:
            validated = validate_ohlcv_bar(bar)
            if normalized_symbol is not None and validated.symbol != normalized_symbol:
                msg = "Provider returned OHLCV bar for a different symbol"
                raise MarketDataValidationError(msg)
            if normalized_timeframe is not None and validated.timeframe != normalized_timeframe:
                msg = "Provider returned OHLCV bar for a different timeframe"
                raise MarketDataValidationError(msg)
            validated_bars.append(validated)

        count = self.candles.upsert_many(validated_bars)
        if commit:
            self.session.commit()
        return count
