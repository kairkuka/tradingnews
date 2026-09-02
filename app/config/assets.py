from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class AssetClass(StrEnum):
    METAL = "METAL"
    INDEX_FUTURE = "INDEX_FUTURE"
    ENERGY = "ENERGY"
    CRYPTO = "CRYPTO"
    FX = "FX"


@dataclass(frozen=True)
class AssetConfig:
    symbol: str
    name: str
    asset_class: AssetClass
    exchange: str | None
    quote_currency: str
    timezone: str
    enabled: bool = True

    @property
    def display_name(self) -> str:
        return self.name


SUPPORTED_ASSETS: Mapping[str, AssetConfig] = MappingProxyType(
    {
        "XAUUSD": AssetConfig("XAUUSD", "Gold", AssetClass.METAL, None, "USD", "UTC"),
        "XAGUSD": AssetConfig("XAGUSD", "Silver", AssetClass.METAL, None, "USD", "UTC"),
        "MNQ": AssetConfig(
            "MNQ",
            "Nasdaq Micro E-mini",
            AssetClass.INDEX_FUTURE,
            "CME",
            "USD",
            "America/Chicago",
        ),
        "NQ": AssetConfig(
            "NQ",
            "Nasdaq E-mini",
            AssetClass.INDEX_FUTURE,
            "CME",
            "USD",
            "America/Chicago",
        ),
        "CL": AssetConfig(
            "CL",
            "Crude Oil WTI",
            AssetClass.ENERGY,
            "NYMEX",
            "USD",
            "America/New_York",
        ),
        "WTI": AssetConfig(
            "WTI",
            "West Texas Intermediate",
            AssetClass.ENERGY,
            None,
            "USD",
            "UTC",
        ),
        "BTCUSDT": AssetConfig("BTCUSDT", "Bitcoin", AssetClass.CRYPTO, None, "USDT", "UTC"),
        "EURUSD": AssetConfig("EURUSD", "Euro / USD", AssetClass.FX, None, "USD", "UTC"),
        "GBPUSD": AssetConfig(
            "GBPUSD",
            "British Pound / USD",
            AssetClass.FX,
            None,
            "USD",
            "UTC",
        ),
        "USDJPY": AssetConfig(
            "USDJPY",
            "USD / Japanese Yen",
            AssetClass.FX,
            None,
            "JPY",
            "UTC",
        ),
        "AUDUSD": AssetConfig(
            "AUDUSD",
            "Australian Dollar / USD",
            AssetClass.FX,
            None,
            "USD",
            "UTC",
        ),
        "USDCAD": AssetConfig(
            "USDCAD",
            "USD / Canadian Dollar",
            AssetClass.FX,
            None,
            "CAD",
            "UTC",
        ),
        "USDCHF": AssetConfig(
            "USDCHF",
            "USD / Swiss Franc",
            AssetClass.FX,
            None,
            "CHF",
            "UTC",
        ),
    }
)

SUPPORTED_SYMBOLS = tuple(SUPPORTED_ASSETS.keys())


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def get_asset(symbol: str) -> AssetConfig | None:
    return SUPPORTED_ASSETS.get(normalize_symbol(symbol))


def require_supported_symbol(symbol: str) -> str:
    normalized = normalize_symbol(symbol)
    if normalized not in SUPPORTED_ASSETS:
        msg = f"Unsupported asset symbol: {symbol}"
        raise ValueError(msg)
    return normalized
