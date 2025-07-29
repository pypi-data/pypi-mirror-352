"""Utilities for working with collections."""

from collections import Counter
from collections.abc import Collection, Iterable, Sized
from typing import Any

from .typevars import T

__all__ = [
    "check_equal_length",
    "get_duplicates",
    "is_collection_of_equal_elements",
]


def check_equal_length(*collections: Sized) -> bool:
    """Given an arbitrary number of collections, check if they all have equal length.

    Args:
        *collections: Objects which have length to be checked for its equality.

    Returns:
        Whether all provided collections have equal length.

    Raises:
        ValueError: If no collections provided.
    """
    if not collections:
        raise ValueError("No collections to provided to check for lengths equality.")
    benchmark_length = len(collections[0])
    return all(len(collection) == benchmark_length for collection in collections)


def get_duplicates(iterable: Iterable[T]) -> frozenset[T]:
    """Get a set of all values in a collection that are duplicates, i.e., present more than once.

    Args:
        iterable: A collection to check.

    Returns:
        A set of values that are present more than once.
    """
    return frozenset(key for key, value in Counter(iterable).items() if value > 1)


def is_collection_of_equal_elements(collection: Collection[Any]) -> bool:
    """Check whether all elements in a collection are equal to each other.

    Args:
        collection: A collection to check that all elements are equal.

    Returns:
        Whether all elements are equal to each other.
    """
    collection = list(collection)
    return all(element == collection[0] for element in collection)
