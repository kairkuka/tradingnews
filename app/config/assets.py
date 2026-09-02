from dataclasses import dataclass


@dataclass(frozen=True)
class AssetConfig:
    symbol: str
    display_name: str
    asset_class: str
    exchange: str | None
    currency: str
    timezone: str
    enabled: bool = True


SUPPORTED_ASSETS: tuple[AssetConfig, ...] = (
    AssetConfig("XAUUSD", "Gold Spot", "metals", None, "USD", "UTC"),
    AssetConfig("XAGUSD", "Silver Spot", "metals", None, "USD", "UTC"),
    AssetConfig(
        "MNQ",
        "Micro E-mini Nasdaq 100 Futures",
        "index_futures",
        "CME",
        "USD",
        "America/Chicago",
    ),
    AssetConfig(
        "NQ",
        "E-mini Nasdaq 100 Futures",
        "index_futures",
        "CME",
        "USD",
        "America/Chicago",
    ),
    AssetConfig("CL", "WTI Crude Oil Futures", "energy", "NYMEX", "USD", "America/New_York"),
    AssetConfig("BTCUSD", "Bitcoin", "crypto", None, "USD", "UTC"),
    AssetConfig("EURUSD", "Euro / US Dollar", "fx", None, "USD", "UTC"),
    AssetConfig("GBPUSD", "British Pound / US Dollar", "fx", None, "USD", "UTC"),
    AssetConfig("USDJPY", "US Dollar / Japanese Yen", "fx", None, "JPY", "UTC"),
    AssetConfig("AUDUSD", "Australian Dollar / US Dollar", "fx", None, "USD", "UTC"),
    AssetConfig("USDCAD", "US Dollar / Canadian Dollar", "fx", None, "CAD", "UTC"),
    AssetConfig("USDCHF", "US Dollar / Swiss Franc", "fx", None, "CHF", "UTC"),
)

SUPPORTED_SYMBOLS = tuple(asset.symbol for asset in SUPPORTED_ASSETS)
