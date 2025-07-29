"""Utilities for text transformations."""

__all__ = [
    "add_suffix",
]


def add_suffix(base: str, suffix: str, separator: str = "_") -> str:
    """Add suffix to a base string using a separator.

    Args:
        base: Base string to add a suffix to.
        suffix: A suffix to add.
        separator: A separator to insert between the base and suffix.

    Returns:
        A string with suffix concatenated to the base on the right, with a separator in between.

    If the suffix is empty, returns just the base string, omitting the separator.
    """
    return f"{base}{separator}{suffix}" if suffix else base
