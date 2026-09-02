SUPPORTED_EVENT_TYPES: tuple[str, ...] = (
    "CPI",
    "Core CPI",
    "PCE",
    "Core PCE",
    "NFP",
    "Unemployment Rate",
    "Average Hourly Earnings",
    "GDP",
    "Retail Sales",
    "ISM Manufacturing PMI",
    "ISM Services PMI",
    "Consumer Confidence",
    "New Home Sales",
    "Existing Home Sales",
    "FOMC Rate Decision",
    "FOMC Statement",
    "Fed Chair Speech",
    "EIA Crude Inventories",
    "API Crude Inventories",
)

EVENT_CATEGORIES: dict[str, tuple[str, ...]] = {
    "inflation": ("CPI", "Core CPI", "PCE", "Core PCE"),
    "employment": ("NFP", "Unemployment Rate", "Average Hourly Earnings"),
    "growth": ("GDP",),
    "business_activity": ("ISM Manufacturing PMI", "ISM Services PMI"),
    "consumer": ("Retail Sales", "Consumer Confidence"),
    "housing": ("New Home Sales", "Existing Home Sales"),
    "federal_reserve": ("FOMC Rate Decision", "FOMC Statement", "Fed Chair Speech"),
    "oil": ("EIA Crude Inventories", "API Crude Inventories"),
}

