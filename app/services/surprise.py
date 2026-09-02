from collections.abc import Sequence
from decimal import Decimal, InvalidOperation


def calculate_surprise(actual: Decimal | None, forecast: Decimal | None) -> Decimal | None:
    if actual is None or forecast is None:
        return None
    return actual - forecast


def calculate_surprise_pct(
    surprise: Decimal | None,
    forecast: Decimal | None,
) -> Decimal | None:
    if surprise is None or forecast is None or forecast == 0:
        return None
    return (surprise / abs(forecast)) * Decimal("100")


def calculate_zscore(
    value: Decimal | None,
    historical_values: Sequence[Decimal],
) -> Decimal | None:
    if value is None or len(historical_values) < 2:
        return None

    mean = sum(historical_values, Decimal("0")) / Decimal(len(historical_values))
    variance = sum((item - mean) ** 2 for item in historical_values) / Decimal(
        len(historical_values)
    )

    try:
        std = variance.sqrt()
    except InvalidOperation:
        return None

    if std == 0:
        return None
    return (value - mean) / std

