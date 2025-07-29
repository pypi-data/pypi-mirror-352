from collections.abc import Collection, Iterable, Sized
from typing import Any

import pytest

from utilsx.collections import (
    check_equal_length,
    get_duplicates,
    is_collection_of_equal_elements,
)
from utilsx.typevars import T


@pytest.mark.parametrize(
    ("input_", "expected_output"),
    (
        ((1,), True),
        ((1, 1), True),
        (((1, 2), (1, 2)), True),
        (({"a": 1}, {"a": 1}), True),
        (((1, 2, 3), (1, 2)), False),
        ((1, "1"), False),
        ((1, 2), False),
        ((1, 1.000001), False),
    ),
)
def test_is_collection_of_equal_elements(input_: Collection[Any], expected_output: bool) -> None:
    assert is_collection_of_equal_elements(input_) == expected_output


@pytest.mark.parametrize(
    ("input_", "expected_output"),
    (
        ((), frozenset()),
        ((1, 2, 3), frozenset()),
        ((1, 2, 3, 1), frozenset((1,))),
        (("a", "b", "c", "a"), frozenset(("a",))),
    ),
)
def test_get_duplicates(input_: Iterable[T], expected_output: frozenset[T]) -> None:
    assert get_duplicates(input_) == expected_output


@pytest.mark.parametrize(
    ("inputs", "expected_output"),
    (
        (((1, 2),), True),
        (((1, 2), ("a", "b")), True),
        (((1, 2), ("a",)), False),
        (((1, 2), ()), False),
    ),
)
def test_check_equal_length(inputs: Collection[Sized], expected_output: bool) -> None:
    assert check_equal_length(*inputs) == expected_output
