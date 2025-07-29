"""Utilities for filtering dictionaries."""

from ..typevars import T

__all__ = [
    "remove_items_with_zero_values",
]


def remove_items_with_zero_values(dictionary: dict[T, float]) -> dict[T, float]:
    """Drop key-value pairs from a dictionary whose values are zero.

    Args:
        dictionary: To be filtered to exclude key-value pairs with zero values.

    Returns:
        A subset of the original dictionary items, only pairs with non-zero values.
    """
    return {key: value for key, value in dictionary.items() if value}
