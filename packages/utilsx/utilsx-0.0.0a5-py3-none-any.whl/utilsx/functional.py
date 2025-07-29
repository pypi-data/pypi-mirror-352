"""Utilities for functional programming."""

from .typevars import T


def identity(x: T) -> T:
    """An identity function: returns a single input unchanged."""
    return x
