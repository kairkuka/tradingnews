from decimal import Decimal

from app.services.bootstrap import bootstrap_confidence_interval, percentile
from app.services.statistics import median, up_probability_statistic


def test_percentile_uses_linear_interpolation() -> None:
    values = (Decimal("-1"), Decimal("0.5"), Decimal("1.5"), Decimal("2"))

    assert percentile(values, Decimal("0.25")) == Decimal("0.125")
    assert percentile(values, Decimal("0.50")) == Decimal("1.00")
    assert percentile(values, Decimal("0.75")) == Decimal("1.625")


def test_bootstrap_interval_handles_constant_win_rate() -> None:
    interval = bootstrap_confidence_interval(
        (Decimal("1"), Decimal("1"), Decimal("1")),
        up_probability_statistic,
        iterations=50,
        seed=1,
    )

    assert interval is not None
    assert interval.lower == Decimal("100")
    assert interval.upper == Decimal("100")


def test_bootstrap_interval_handles_constant_median() -> None:
    interval = bootstrap_confidence_interval(
        (Decimal("2"), Decimal("2"), Decimal("2")),
        median,
        iterations=50,
        seed=1,
    )

    assert interval is not None
    assert interval.lower == Decimal("2")
    assert interval.upper == Decimal("2")

