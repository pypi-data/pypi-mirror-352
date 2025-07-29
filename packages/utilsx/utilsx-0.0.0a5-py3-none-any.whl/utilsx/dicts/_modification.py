"""Utils for modifying keys or values of dictionaries."""

from collections.abc import Mapping
from typing import Any

from ..typevars import T

__all__ = [
    "multiply_dict_values",
    "rename_keys_in_nested_dict",
]


def multiply_dict_values(dictionary: Mapping[T, float], multiplier: float) -> dict[T, float]:
    """Get a copy of the dictionary with values multiplied by scalar, preserving keys.

    Args:
        dictionary: A dictionary to multiply values of.
        multiplier: A scalar multiplier.

    Returns:
        A copy of the original dictionary with values multiplied by scalar.
    """
    return {key: value * multiplier for key, value in dictionary.items()}


def rename_keys_in_nested_dict(
    dictionary: dict[str, Any], renaming: dict[str, str]
) -> dict[str, Any]:
    """Replace all specified keys by other specified names in an arbitrarily deep dictionary.

    Args:
        dictionary: A dictionary of arbitrary depth.
        renaming: A mapping from old to new key names.

    Returns:
        Copy of the original dictionary with ``old_key`` renamed to ``new_key``
        at all levels of key depth.
    """
    # This ``isinstance`` check is required to leave non-dict structures as-is.
    if isinstance(dictionary, dict):
        return {
            (renaming.get(key, key)): rename_keys_in_nested_dict(value, renaming)
            for key, value in dictionary.items()
        }
    return dictionary
