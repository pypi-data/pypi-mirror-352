"""Utilities for division."""

__all__ = [
    "safe_divide",
]


def safe_divide(numerator: float, denominator: float, fallback: float = 0) -> float:
    """Divide one number by another, falling back on something in case of ``ZeroDivisionError``.

    Args:
        numerator: Number to divide.
        denominator: Denominator to use.
        fallback: Fallback value to use in case the denominator is zero, defaults to zero.
    """
    return numerator / denominator if denominator != 0 else fallback
