"""The main process function."""

import pandas as pd

from .feature import Feature
from .lag_process import lag_process
from .non_categorical_numeric_columns import \
    find_non_categorical_numeric_columns
from .rolling_process import rolling_process
from .shift_process import shift_process


def process(
    df: pd.DataFrame,
    features: list[Feature],
    on: str | None = None,
    shift: int = 1,
) -> pd.DataFrame:
    """Process the dataframe for timeseries features."""
    original_columns = df.columns.values.tolist()
    valid_columns = find_non_categorical_numeric_columns(df)
    df = lag_process(df, features, valid_columns)
    lagged_columns = [
        x for x in df.columns.values.tolist() if x not in original_columns
    ]
    df = rolling_process(df, features, on, valid_columns)
    added_features = [
        x
        for x in df.columns.values.tolist()
        if x not in original_columns and x not in lagged_columns
    ]
    df = shift_process(df, valid_columns + added_features, shift)
    return df[sorted(df.columns.values.tolist())]
