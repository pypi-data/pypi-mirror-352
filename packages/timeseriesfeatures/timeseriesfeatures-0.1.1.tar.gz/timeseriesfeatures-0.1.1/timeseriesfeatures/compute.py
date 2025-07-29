"""The function for automatically computing features."""

import pandas as pd

from .compute_acf import compute_acf
from .compute_nbeats import compute_nbeats
from .compute_pacf import compute_pacf
from .feature import Feature
from .non_categorical_numeric_columns import \
    find_non_categorical_numeric_columns


def compute(
    df: pd.DataFrame,
    max_lag: int,
    min_lag: int,
) -> list[Feature]:
    """Process the dataframe for determining timeseries features."""
    features = []
    columns = find_non_categorical_numeric_columns(df)
    for column in columns:
        series = df[column]
        for compute_func in [compute_acf, compute_pacf, compute_nbeats]:
            features.extend(compute_func(series, max_lag, min_lag))
    return features
