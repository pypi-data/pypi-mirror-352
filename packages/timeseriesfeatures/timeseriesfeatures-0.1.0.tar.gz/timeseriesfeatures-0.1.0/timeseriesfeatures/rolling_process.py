"""Calculate rolling features."""

# pylint: disable=too-many-branches,too-many-statements
import datetime

import pandas as pd

from .columns import (ALL_SUFFIX, COUNT_WINDOW_FUNCTION, DAYS_COLUMN_SUFFIX,
                      DELIMITER, KURT_WINDOW_FUNCTION, MAX_WINDOW_FUNCTION,
                      MEAN_WINDOW_FUNCTION, MEDIAN_WINDOW_FUNCTION,
                      MIN_WINDOW_FUNCTION, RANK_WINDOW_FUNCTION,
                      SEM_WINDOW_FUNCTION, SKEW_WINDOW_FUNCTION,
                      STD_WINDOW_FUNCTION, SUM_WINDOW_FUNCTION,
                      TRANSFORM_COLUMN, VAR_WINDOW_FUNCTION, WINDOW_FUNCTIONS)
from .feature import (FEATURE_TYPE_ROLLING, VALUE_TYPE_DAYS, VALUE_TYPE_INT,
                      Feature)
from .transforms import TRANSFORMS


def rolling_process(
    df: pd.DataFrame,
    features: list[Feature],
    on: str | None,
    columns: list[str],
) -> pd.DataFrame:
    """Process margins between teams."""
    if not features:
        return df
    for column in columns:
        for feature in features:
            if feature["feature_type"] != FEATURE_TYPE_ROLLING:
                continue
            if feature["columns"] and column not in feature["columns"]:
                continue
            input_type = feature["value1"]
            if "value2" not in feature:
                continue
            input_value = feature["value2"]
            window: int | datetime.timedelta | None = None
            if input_value is not None:
                if input_type == VALUE_TYPE_INT:
                    window = int(input_value)
                elif input_type == VALUE_TYPE_DAYS:
                    window = datetime.timedelta(days=int(input_value))
            window_df = df[[column] + [] if on is None else [on]].copy()
            window_df[column] = TRANSFORMS[feature["transform"]](df[column])
            window_df = (
                window_df.rolling(window, on=on)  # type: ignore
                if window is not None
                else window_df.expanding()
            )
            window_df = window_df[column]  # type: ignore
            window_col = ALL_SUFFIX
            if isinstance(window, int):
                window_col = str(window)
            elif isinstance(window, datetime.timedelta):
                window_col = str(window.days) + DAYS_COLUMN_SUFFIX
            for window_func in WINDOW_FUNCTIONS:
                new_column = DELIMITER.join(
                    [
                        column,
                        TRANSFORM_COLUMN,
                        feature["transform"],
                        window_func,
                        window_col,
                    ]
                )
                if window_func == COUNT_WINDOW_FUNCTION:
                    df[new_column] = window_df.count()
                elif window_func == SUM_WINDOW_FUNCTION:
                    df[new_column] = window_df.sum()
                elif window_func == MEAN_WINDOW_FUNCTION:
                    df[new_column] = window_df.mean()
                elif window_func == MEDIAN_WINDOW_FUNCTION:
                    df[new_column] = window_df.median()
                elif window_func == VAR_WINDOW_FUNCTION:
                    df[new_column] = window_df.var()
                elif window_func == STD_WINDOW_FUNCTION:
                    df[new_column] = window_df.std()
                elif window_func == MIN_WINDOW_FUNCTION:
                    df[new_column] = window_df.min()
                elif window_func == MAX_WINDOW_FUNCTION:
                    df[new_column] = window_df.max()
                elif window_func == SKEW_WINDOW_FUNCTION:
                    df[new_column] = window_df.skew()
                elif window_func == KURT_WINDOW_FUNCTION:
                    df[new_column] = window_df.kurt()
                elif window_func == SEM_WINDOW_FUNCTION:
                    df[new_column] = window_df.sem()
                elif window_func == RANK_WINDOW_FUNCTION:
                    df[new_column] = window_df.rank()
                else:
                    raise ValueError(f"Unrecognised window function: {window_func}")
    return df
