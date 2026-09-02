ASSET_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "XAUUSD": ("DXY", "US10Y", "XAGUSD", "VIX"),
    "XAGUSD": ("XAUUSD", "DXY", "US10Y", "MNQ"),
    "MNQ": ("US10Y", "DXY", "VIX", "BTCUSD"),
    "NQ": ("US10Y", "DXY", "VIX", "BTCUSD"),
    "BTCUSD": ("MNQ", "DXY", "US10Y", "VIX"),
    "CL": ("USDCAD", "DXY", "EIA Crude Inventories"),
    "USDCAD": ("CL", "DXY", "US10Y"),
}

