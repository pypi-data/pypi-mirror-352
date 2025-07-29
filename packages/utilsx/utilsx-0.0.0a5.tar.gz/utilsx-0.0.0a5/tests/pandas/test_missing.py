import pandas as pd
import pytest

from utilsx.pandas import count_na


@pytest.mark.parametrize(
    ("df", "expected"),
    (
        (pd.DataFrame(), 0),
        (pd.DataFrame({"a": (0, 1)}), 0),
        (pd.DataFrame({"name": ("John", None)}), 1),
        (pd.DataFrame({"sales": (1, float("nan"), float("nan"))}), 2),
    ),
)
def test_count_na(df: pd.DataFrame, expected: int) -> None:
    assert count_na(df) == expected
