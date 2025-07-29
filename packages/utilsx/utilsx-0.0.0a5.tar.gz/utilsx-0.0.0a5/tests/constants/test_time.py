from utilsx.constants._time import HOURS_IN_YEAR, MINUTES_IN_WEEK


def test_time() -> None:
    """Test that calculated time constants match known ground truth values."""
    assert HOURS_IN_YEAR == 8760
    assert MINUTES_IN_WEEK == 10080
