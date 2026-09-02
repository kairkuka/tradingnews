from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candle
from app.providers.market.schemas import OhlcvBar, ensure_utc_timestamp, validate_ohlcv_bar


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
        start: datetime | None = None,
        end: datetime | None = None,
        *,
        include_start: bool = True,
        include_end: bool = True,
    ) -> tuple[Candle, ...]:
        conditions = [Candle.symbol == symbol, Candle.timeframe == timeframe]
        if start is not None:
            utc_start = ensure_utc_timestamp(start)
            if include_start:
                conditions.append(Candle.timestamp >= utc_start)
            else:
                conditions.append(Candle.timestamp > utc_start)
        if end is not None:
            utc_end = ensure_utc_timestamp(end)
            if include_end:
                conditions.append(Candle.timestamp <= utc_end)
            else:
                conditions.append(Candle.timestamp < utc_end)

        rows = self.session.scalars(
            select(Candle)
            .where(*conditions)
            .order_by(Candle.timestamp)
        )
        return tuple(rows)

    def last_before(
        self,
        symbol: str,
        timeframe: str,
        before: datetime,
    ) -> Candle | None:
        utc_before = ensure_utc_timestamp(before)
        return self.session.scalars(
            select(Candle)
            .where(
                Candle.symbol == symbol,
                Candle.timeframe == timeframe,
                Candle.timestamp < utc_before,
            )
            .order_by(Candle.timestamp.desc())
            .limit(1)
        ).first()
