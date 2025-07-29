"""Utilities for analyzing, or dealing with missing values."""

import pandas as pd

__all__ = [
    "count_na",
]


def count_na(df: pd.DataFrame) -> int:
    """Get the total number of missing values in a DataFrame.

    Args:
        df: To count missing values in.

    Returns:
        The number of missing values.
    """
    return int(df.isna().sum().sum())
