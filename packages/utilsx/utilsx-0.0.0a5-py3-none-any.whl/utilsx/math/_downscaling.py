"""Utilities for downscaling numbers - e.g., converting to thousands."""

from typing import Literal

from utilsx.constants import MILLION, THOUSAND

__all__ = [
    "convert_number_to_units",
]

_TUnits = Literal["thousand", "million"]


def convert_number_to_units(number: float, units: _TUnits) -> float:
    """Convert a number to thousands or millions.

    Args:
        number: Number to convert.
        units: Units to convert to.

    Returns:
        A number converted to specified units.
    """
    match units:
        case "thousand":
            denominator = THOUSAND
        case "million":
            denominator = MILLION
        case _:
            raise ValueError(f"Unrecognized units: {units}")

    return number / denominator
