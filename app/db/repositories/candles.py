from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candle
from app.providers.market.schemas import OhlcvBar, validate_ohlcv_bar


class CandleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, bar: OhlcvBar) -> Candle:
        validated = validate_ohlcv_bar(bar)
        existing = self.session.execute(
            select(Candle).where(
                Candle.symbol == validated.symbol,
                Candle.timeframe == validated.timeframe,
                Candle.timestamp == validated.timestamp,
            )
        ).scalar_one_or_none()

        if existing is None:
            candle = Candle(
                symbol=validated.symbol,
                timeframe=validated.timeframe,
                timestamp=validated.timestamp,
                open=validated.open,
                high=validated.high,
                low=validated.low,
                close=validated.close,
                volume=validated.volume,
            )
            self.session.add(candle)
            return candle

        existing.open = validated.open
        existing.high = validated.high
        existing.low = validated.low
        existing.close = validated.close
        existing.volume = validated.volume
        return existing

    def upsert_many(self, bars: Iterable[OhlcvBar]) -> int:
        count = 0
        for bar in bars:
            self.upsert(bar)
            count += 1
        return count

    def list_range(
        self,
        symbol: str,
        timeframe: str,
    ) -> tuple[Candle, ...]:
        rows = self.session.scalars(
            select(Candle)
            .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
            .order_by(Candle.timestamp)
        )
        return tuple(rows)

