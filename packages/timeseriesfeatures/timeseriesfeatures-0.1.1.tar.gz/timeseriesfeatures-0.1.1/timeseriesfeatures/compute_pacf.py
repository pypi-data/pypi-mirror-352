"""Compute partial auto-correlated features."""

# pylint: disable=duplicate-code
import pandas as pd
from statsmodels.tsa.stattools import pacf  # type: ignore

from .compute_acf import sort_acf_vals
from .feature import FEATURE_TYPE_LAG, VALUE_TYPE_INT, Feature
from .transform import Transform


def compute_pacf(series: pd.Series, max_lag: int, min_lag: int) -> list[Feature]:
    """Compute partial auto-correlated features."""
    acf_vals = pacf(series, nlags=max_lag)
    features = []
    for lag in sort_acf_vals(acf_vals, min_lag):  # type: ignore
        new_feature = Feature(
            feature_type=FEATURE_TYPE_LAG,
            columns=[str(series.name)],
            value1=VALUE_TYPE_INT,
            value2=lag,
            transform=str(Transform.NONE),
        )
        if new_feature in features:
            continue
        features.append(new_feature)
    return features
