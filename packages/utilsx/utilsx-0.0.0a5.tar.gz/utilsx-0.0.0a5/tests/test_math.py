from collections.abc import Collection, Sequence
from typing import Literal

import pytest

from utilsx.math import (
    ceil_to_multiple,
    check_values_add_up_to_one,
    double,
    halve,
    is_monotonically_growing,
    normalize,
    safe_divide,
)


@pytest.mark.parametrize(
    ("x", "expected"),
    (
        (10, 5),
        (3, 1.5),
        (0, 0),
        (-8, -4),
        (-3.6, -1.8),
        (7.5, 3.75),
        (1, 0.5),
        (-1, -0.5),
        (1000000, 500000),
    ),
)
def test_halve(x: float, expected: float) -> None:
    assert halve(x) == expected


@pytest.mark.parametrize(
    ("x", "expected"),
    (
        (10, 20),
        (3, 6),
        (0, 0),
        (-8, -16),
        (-3.6, -7.2),
        (7.5, 15),
        (1, 2),
        (-1, -2),
        (1000000, 2000000),
    ),
)
def test_double(x: float, expected: float) -> None:
    assert double(x) == expected


@pytest.mark.parametrize(
    ("input_", "expected_output"),
    (
        ((0.5, 0.5), [0.5, 0.5]),
        ([3, 2], [0.6, 0.4]),
        ((0, 42), [0, 1]),
    ),
)
def test_normalize(input_: Sequence[float], expected_output: list[float]) -> None:
    assert normalize(input_) == expected_output


@pytest.mark.parametrize(
    ("x", "multiple", "expected"),
    (
        (23, 5, 25),
        (12, 7, 14),
        (47, 10, 50),
        (0, 5, 0),
        (-4, 3, -3),
        (-10, 4, -8),
        (15.2, 5, 20),
        (99, 1, 99),
        (100, 25, 100),
    ),
)
def test_ceil_to_multiple(x: float, multiple: int, expected: int) -> None:
    assert ceil_to_multiple(x, multiple) == expected


@pytest.mark.parametrize(
    ("values", "mode", "expected"),
    (
        # Fractions mode
        ([0.5, 0.5], "fractions", True),
        ([1.0], "fractions", True),
        ([0.333, 0.333, 0.334], "fractions", True),
        ([0.9, 0.05], "fractions", False),
        ([100], "fractions", False),
        # Percentages mode
        ([50, 50], "percentages", True),
        ([99.9, 0.1], "percentages", True),
        ([101], "percentages", False),
        ([1], "percentages", False),
        # Either mode
        ([1], "either", True),
        ([100], "either", True),
        ([0.5, 0.5], "either", True),
        ([50, 50], "either", True),
        ([0.1, 0.2, 0.3], "either", False),
        # Edge cases
        ([], "fractions", False),
        ([0, 0, 0], "percentages", False),
        ([1e-10, 1e-10], "fractions", False),
        ([33.3, 33.3, 33.4], "percentages", True),
        # Various collection types
        ((0.5, 0.5), "fractions", True),
        ({0.2, 0.8}, "fractions", True),
        (frozenset((0.2, 0.8)), "fractions", True),
    ),
)
def test_check_values_add_up_to_one(
    values: Collection[float],
    mode: Literal["fractions", "percentages", "either"],
    expected: bool,
) -> None:
    assert check_values_add_up_to_one(values, mode) is expected


@pytest.mark.parametrize(
    ("numerator", "denominator", "fallback", "expected"),
    (
        (10, 2, 0, 5),  # Normal division
        (7, 0, 0, 0),  # By zero with zero as fallback
        (7, 0, -1, -1),  # By zero with custom fallback
        (0, 3, 0, 0),  # Zero numerator
        (-6, 2, 0, -3),  # Negative numerator
        (6, -2, 0, -3),  # Negative denominator
        (-6, -2, 0, 3),  # Both negative
        (1e10, 1e5, 0, 1e5),  # Large numbers
    ),
)
def test_safe_divide(
    numerator: float,
    denominator: float,
    fallback: float,
    expected: float,
) -> None:
    assert safe_divide(numerator, denominator, fallback) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("time_series", "known_answer"),
    (
        ((1,), False),
        ((1, 2), True),
        ((1, 2, 3), True),
        ((1, 1.2, 1.5), True),
        ((1, 2, 2), False),
        ((1, 1.01, 1.02), False),
        ((1, 2, 3, 4, 5, 1), False),
    ),
)
def test_is_monotonically_growing(
    time_series: tuple[float],
    known_answer: bool,
) -> None:
    assert is_monotonically_growing(time_series, 1.1) == known_answer
