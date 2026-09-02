from decimal import Decimal

from app.services.surprise import calculate_surprise, calculate_surprise_pct, calculate_zscore


def test_calculate_surprise_and_percentage() -> None:
    surprise = calculate_surprise(Decimal("3.1"), Decimal("3.3"))

    assert surprise == Decimal("-0.2")
    assert calculate_surprise_pct(surprise, Decimal("3.3")) == Decimal(
        "-6.060606060606060606060606061"
    )


def test_calculate_zscore_uses_historical_mean_and_std() -> None:
    zscore = calculate_zscore(Decimal("4"), (Decimal("1"), Decimal("3")))

    assert zscore == Decimal("2")


def test_calculate_zscore_returns_none_without_enough_history() -> None:
    assert calculate_zscore(Decimal("4"), (Decimal("1"),)) is None
    assert calculate_zscore(Decimal("4"), (Decimal("2"), Decimal("2"))) is None

