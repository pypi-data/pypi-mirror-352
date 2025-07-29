import pytest

from utilsx.text import add_suffix


@pytest.mark.parametrize(
    ("base", "suffix", "expected"),
    (
        ("plan", "", "plan"),
        ("plan", "a", "plan_a"),
        ("plan", "B", "plan_B"),
    ),
)
def test_add_suffix(base: str, suffix: str, expected: str) -> None:
    assert add_suffix(base, suffix) == expected
