from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.providers.market.schemas import OhlcvBar, Quote


class MarketDataProvider(ABC):
    @abstractmethod
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[OhlcvBar]:
        """Return OHLCV bars with UTC-aware timestamps."""

    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Decimal:
        """Return latest traded/reference price for a supported symbol."""

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Return latest quote for a supported symbol."""

