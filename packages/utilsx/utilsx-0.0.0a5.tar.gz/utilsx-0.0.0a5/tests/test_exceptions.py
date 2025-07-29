from collections.abc import Collection, Iterable

import pytest

from utilsx.exceptions import prohibit_negative_values, raise_key_error_with_suggestions


@pytest.mark.parametrize(
    ("values", "should_fail"),
    (
        ([0, 1, 2], False),
        ((0.0, 3.14, 100), False),
        ([], False),
        ([-1], True),
        (frozenset((0, -1, 2)), True),
        ([0.0, -3.14], True),
    ),
)
def test_prohibit_negative_values(values: Iterable[float], should_fail: bool) -> None:
    if should_fail:
        with pytest.raises(ValueError, match="prohibited"):
            prohibit_negative_values(values)
    else:
        prohibit_negative_values(values)


def test_prohibit_negative_values_custom_exception() -> None:
    """Test that a custom exception is being raised if asked so."""
    with pytest.raises(FileNotFoundError, match="weird"):
        prohibit_negative_values(
            values=(-1, 1),
            exception_class=FileNotFoundError,
            exception_msg="Let's see if this weird exception class is raised too",
        )


@pytest.mark.parametrize(
    ("attempted_key", "existing_keys", "object_name", "attribute_name", "expected_message"),
    (
        (
            "frut",
            ["fruit", "vegetable", "meat"],
            "basket",
            "item",
            "Basket with item frut not found. Did you mean one of these instead: fruit?",
        ),
        (
            "apple",
            ["banana", "carrot"],
            "box",
            "fruit",
            "Box with fruit apple not found.",
        ),
        (
            "hundai",
            ["bmw", "hyundai", "audi"],
            "car",
            "brand",
            "Car with brand hundai not found. Did you mean one of these instead: hyundai?",
        ),
    ),
)
def test_raise_key_error_with_suggestions(
    attempted_key: str,
    existing_keys: Collection[str],
    object_name: str,
    attribute_name: str,
    expected_message: str,
) -> None:
    with pytest.raises(KeyError) as exc_info:
        raise_key_error_with_suggestions(
            attempted_key=attempted_key,
            existing_keys=existing_keys,
            object_name=object_name,
            attribute_name=attribute_name,
        )
    received_message = exc_info.value.args[0]
    assert received_message == expected_message
