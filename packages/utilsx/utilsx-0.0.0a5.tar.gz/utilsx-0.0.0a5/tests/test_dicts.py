from collections.abc import Collection
from typing import Any

import pytest

from utilsx.dicts import rename_keys_in_nested_dict, sort_by_value, sum_dicts


@pytest.mark.parametrize(
    ("dictionary", "reverse", "output"),
    (
        ({"a": 1, "b": 2}, True, {"b": 2, "a": 1}),
        ({False: 1, True: 2}, True, {True: 2, False: 1}),
        ({"a": 1, "b": 3, "c": 2}, False, {"a": 1, "c": 2, "b": 3}),
        ({"a": 1}, False, {"a": 1}),
        ({"a": 1}, True, {"a": 1}),
        ({}, True, {}),
    ),
)
def test_sort_by_value(
    dictionary: dict[Any, float],
    reverse: bool,
    output: dict[Any, float],
) -> None:
    assert tuple(sort_by_value(dictionary, reverse)) == tuple(output)


@pytest.mark.parametrize(
    ("inputs", "output"),
    (
        (({"a": 1, "b": 2}, {"c": 3}), {"a": 1, "b": 2, "c": 3}),
        (({"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}), {"a": 2, "b": 4, "c": 3}),
        (({}, {}), {}),
        (({"a": 1},) * 3, {"a": 3}),
    ),
)
def test_sum_dicts(
    inputs: Collection[dict[Any, float]],
    output: dict[Any, float],
) -> None:
    assert sum_dicts(*inputs) == output


def test_rename_keys_in_nested_dict() -> None:
    before = {
        "db_config": {
            "usr": "admin",
            "pwd": "secret",
            "host": "localhost",
            "port": 5432,
        },
        "log_settings": {
            "lvl": "INFO",
            "dir": "/var/log/app",
            "otel_credentials": {
                "usr": "otel_admin",
                "pwd": "otel_password",
            },
        },
    }
    renaming = {
        "usr": "user",
        "pwd": "password",
    }
    after = rename_keys_in_nested_dict(before, renaming)
    assert after["db_config"]["user"]
    assert after["db_config"]["password"]
    assert frozenset(after["log_settings"]["otel_credentials"]) == frozenset(("user", "password"))
