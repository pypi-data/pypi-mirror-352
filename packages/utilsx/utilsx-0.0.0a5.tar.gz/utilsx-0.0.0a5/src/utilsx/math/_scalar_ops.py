"""Simple operations on scalars - individual values."""

__all__ = [
    "double",
    "halve",
]


def double(x: float) -> float:
    """Multiply a number by two: in other words, double it.

    Args:
        x: The number to multiply by two.

    Returns:
        Result of multiplying this number by literal integer two.
    """
    return x * 2


def halve(x: float) -> float:
    """Divide a number by two: in other words, get its half.

    Args:
        x: The number to divide by two.

    Returns:
        Result of dividing this number by literal integer two.
    """
    return x / 2
