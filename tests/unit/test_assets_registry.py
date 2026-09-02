import pytest

from app.config.assets import (
    SUPPORTED_ASSETS,
    AssetClass,
    get_asset,
    require_supported_symbol,
)


def test_supported_asset_registry_matches_phase_2_scope() -> None:
    assert set(SUPPORTED_ASSETS) == {
        "XAUUSD",
        "XAGUSD",
        "MNQ",
        "NQ",
        "CL",
        "WTI",
        "BTCUSDT",
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "AUDUSD",
        "USDCAD",
        "USDCHF",
    }


def test_asset_metadata_uses_config_registry() -> None:
    gold = get_asset("xauusd")

    assert gold is not None
    assert gold.name == "Gold"
    assert gold.asset_class == AssetClass.METAL
    assert gold.quote_currency == "USD"


def test_require_supported_symbol_normalizes_and_rejects_unknown() -> None:
    assert require_supported_symbol(" btcusdt ") == "BTCUSDT"

    with pytest.raises(ValueError, match="Unsupported asset symbol"):
        require_supported_symbol("AAPL")

