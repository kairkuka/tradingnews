from collections.abc import Callable, Sequence
from decimal import Decimal
from random import Random

from app.services.statistics_schemas import BootstrapInterval

StatisticFunction = Callable[[Sequence[Decimal]], Decimal | None]


def bootstrap_confidence_interval(
    values: Sequence[Decimal],
    statistic: StatisticFunction,
    *,
    confidence: Decimal = Decimal("0.95"),
    iterations: int = 500,
    seed: int = 42,
) -> BootstrapInterval | None:
    if not values or iterations < 1:
        return None

    rng = Random(seed)
    estimates: list[Decimal] = []
    for _ in range(iterations):
        sample = tuple(values[rng.randrange(len(values))] for _ in values)
        estimate = statistic(sample)
        if estimate is not None:
            estimates.append(estimate)

    if not estimates:
        return None

    alpha = Decimal("1") - confidence
    lower = percentile(estimates, alpha / Decimal("2"))
    upper = percentile(estimates, Decimal("1") - (alpha / Decimal("2")))
    if lower is None or upper is None:
        return None
    return BootstrapInterval(lower=lower, upper=upper)


def percentile(values: Sequence[Decimal], quantile: Decimal) -> Decimal | None:
    if not values:
        return None
    if quantile < 0 or quantile > 1:
        msg = "quantile must be between 0 and 1"
        raise ValueError(msg)

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    position = quantile * Decimal(len(ordered) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = position - Decimal(lower_index)
    return ordered[lower_index] + ((ordered[upper_index] - ordered[lower_index]) * fraction)

