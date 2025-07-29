"""An derivative transform."""

import functools
from typing import Callable

import pandas as pd


def derivative_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by derivative."""
    return series.pct_change()


def create_derivative_transform(derivative: int) -> Callable[[pd.Series], pd.Series]:
    """Creates a function determining the Nth order derivative."""

    def _recursive_derivative_transform(
        series: pd.Series, derivative: int
    ) -> pd.Series:
        for _ in range(derivative):
            series = derivative_transform(series)
        return series

    return functools.partial(_recursive_derivative_transform, derivative=derivative)
