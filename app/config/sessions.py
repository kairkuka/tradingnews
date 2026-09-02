from collections.abc import Mapping
from dataclasses import dataclass
from datetime import time
from types import MappingProxyType


@dataclass(frozen=True)
class SessionWindow:
    name: str
    start: time
    end: time
    timezone: str


FUTURES_SESSIONS: Mapping[str, SessionWindow] = MappingProxyType(
    {
        "RTH": SessionWindow("RTH", time(8, 30), time(15, 0), "America/Chicago"),
        "ETH": SessionWindow("ETH", time(17, 0), time(16, 0), "America/Chicago"),
    }
)

GLOBAL_SESSIONS: Mapping[str, SessionWindow] = MappingProxyType(
    {
        "Asia": SessionWindow("Asia", time(0, 0), time(8, 0), "UTC"),
        "London": SessionWindow("London", time(7, 0), time(16, 0), "UTC"),
        "New York": SessionWindow("New York", time(12, 0), time(21, 0), "UTC"),
        "Overnight": SessionWindow("Overnight", time(21, 0), time(7, 0), "UTC"),
    }
)

