"""An SMA transform."""

import functools
from typing import Callable

import pandas as pd


def sma_transform(series: pd.Series, window: int) -> pd.Series:
    """Transforms a series by SMA."""
    return series.rolling(window=window).mean()


def create_sma_transform(window: int) -> Callable[[pd.Series], pd.Series]:
    """Creates a function determining the SMA with the window."""
    return functools.partial(sma_transform, window=window)
