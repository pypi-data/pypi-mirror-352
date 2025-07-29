"""Utilities for combining dictionaries."""

from collections import defaultdict

from ..typevars import T

__all__ = [
    "sum_dicts",
]


def sum_dicts(*dicts: dict[T, float]) -> dict[T, float]:
    """Given dictionaries, return their summation: a union of keys and totals of values.

    Args:
        *dicts: To be added up together, any number.

    Returns:
        A combined dictionary with a union of keys and totals of values.
    """
    output: dict[T, float] = defaultdict(float)
    for dictionary in dicts:
        for key, value in dictionary.items():
            output[key] += value
    return dict(output)
