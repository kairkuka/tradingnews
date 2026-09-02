from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime

from app.providers.economic.schemas import EconomicCalendarEvent


class EconomicCalendarProvider(ABC):
    @abstractmethod
    async def get_upcoming_events(
        self,
        start: datetime,
        end: datetime,
        *,
        countries: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
    ) -> Sequence[EconomicCalendarEvent]:
        """Return upcoming economic events with UTC-aware timestamps."""

    @abstractmethod
    async def get_historical_events(
        self,
        start: datetime,
        end: datetime,
        *,
        countries: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
    ) -> Sequence[EconomicCalendarEvent]:
        """Return historical economic events with actual/forecast/previous values when available."""

    @abstractmethod
    async def get_event(self, provider_event_id: str) -> EconomicCalendarEvent:
        """Return one provider event by provider-native id."""

