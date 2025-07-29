import pytest

from utilsx.constants._numbers import BILLION, MILLION, ONE, TEN, THOUSAND, TRILLION, TWO


@pytest.mark.parametrize(
    ("one", "another"),
    (
        (ONE * TEN, TEN),
        (TEN * TWO, 20),
        (BILLION / THOUSAND, MILLION),
        (MILLION * MILLION, TRILLION),
    ),
)
def test_numbers(one: float, another: float) -> None:
    """Test that numeric constants are mutually consistent."""
    assert one == another
