"""Math operations on collections of values."""

import math
from collections.abc import Collection, Sequence
from typing import Literal

__all__ = [
    "check_values_add_up_to_one",
    "is_monotonically_growing",
    "normalize",
]


def check_values_add_up_to_one(
    values: Collection[float],
    mode: Literal["fractions", "percentages", "either"] = "either",
) -> bool:
    """Check if values in a collection add up to 1 or 100.

    Args:
        values: Values to check.
        mode: "fractions" if they should add up to 1, "percentages" if they should add up to 100,
            "either" if either of this works.

    Returns:
        Boolean outcome of the check.
    """
    match mode:
        case "fractions":
            valid_totals = frozenset((1,))
        case "percentages":
            valid_totals = frozenset((100,))
        case "either":
            valid_totals = frozenset((1, 100))
        case _:
            raise ValueError(f"Unrecognized mode: {mode}")

    sum_of_values = sum(values)
    return any(
        math.isclose(sum_of_values, valid_total, rel_tol=0.001) for valid_total in valid_totals
    )


def is_monotonically_growing(time_series: Sequence[float], multiplier: float) -> bool:
    """Check whether a time series can be considered monotonically growing.

    To be called so, each next element should be at least ``multiplier`` times bigger than
    a previous one. Series of less than two elements are considered non-growing.

    Args:
        time_series: A sequence of numbers.
        multiplier: How many times bigger each next element should be.

    Returns:
        True if monotonically growing, False otherwise.
    """
    if len(time_series) < 2:  # noqa: PLR2004
        return False
    return all(
        time_series[i + 1] > time_series[i] * multiplier for i in range(len(time_series) - 1)
    )


def normalize(values: Sequence[float]) -> list[float]:
    """Normalize a sequence of numbers to make them add up to one."""
    return [value / sum(values) for value in values]
