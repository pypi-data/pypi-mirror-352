"""A log transform."""

import numpy as np
import pandas as pd


def log_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by log."""
    return np.log1p(series.clip(lower=0))  # type: ignore
