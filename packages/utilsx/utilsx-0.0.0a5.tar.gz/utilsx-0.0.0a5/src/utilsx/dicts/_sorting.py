"""Utils for sorting dictionaries."""

from ..typevars import NumberT, T

__all__ = [
    "sort_by_value",
]


def sort_by_value(dictionary: dict[T, NumberT], reverse: bool = False) -> dict[T, NumberT]:
    """Sort a dictionary with numeric values by those values.

    Args:
        dictionary: A dictionary to sort by value.
        reverse: False for ascending order, True for descending. Exactly matches the ``reverse``
            argument of ``sorted`` Python function.

    Returns:
        Same dictionary in terms of content, just sorted by value.
    """
    return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))
