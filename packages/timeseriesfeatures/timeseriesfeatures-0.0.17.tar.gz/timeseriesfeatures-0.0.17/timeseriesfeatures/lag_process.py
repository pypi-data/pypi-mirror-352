"""Calculate lag features."""

import pandas as pd

from .columns import DELIMITER, LAG_COLUMN, TRANSFORM_COLUMN
from .feature import FEATURE_TYPE_LAG, Feature
from .transforms import TRANSFORMS


def lag_process(
    df: pd.DataFrame, features: list[Feature], columns: list[str]
) -> pd.DataFrame:
    """Process margins between teams."""
    if not features:
        return df
    for column in columns:
        for feature in features:
            if feature["feature_type"] != FEATURE_TYPE_LAG:
                continue
            if feature["columns"] and column not in feature["columns"]:
                continue
            lag = feature["value1"]
            if not isinstance(lag, int):
                continue
            new_column = DELIMITER.join(
                [column, TRANSFORM_COLUMN, feature["transform"], LAG_COLUMN, str(lag)]
            )
            df[new_column] = TRANSFORMS[feature["transform"]](df[column]).shift(lag)
    return df
