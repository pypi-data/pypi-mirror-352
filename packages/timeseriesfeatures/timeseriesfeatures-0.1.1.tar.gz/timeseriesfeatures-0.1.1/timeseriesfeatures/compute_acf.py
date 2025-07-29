"""Compute auto-correlated features."""

import pandas as pd
from statsmodels.tsa.stattools import acf  # type: ignore

from .feature import FEATURE_TYPE_LAG, VALUE_TYPE_INT, Feature
from .transform import Transform


def sort_acf_vals(acf_vals: list[float], min_lag: int) -> list[int]:
    """Sort auto-correlation values."""
    return [
        lag
        for lag, val in sorted(
            [
                (lag, val)
                for lag, val in enumerate(acf_vals)
                if abs(val) > 0.3 and lag != 0 and lag > min_lag
            ],
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:4]
    ]


def compute_acf(series: pd.Series, max_lag: int, min_lag: int) -> list[Feature]:
    """Compute auto-correlated features."""
    acf_vals = acf(series, nlags=max_lag, fft=False)
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
