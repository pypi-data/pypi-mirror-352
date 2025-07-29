"""Calculate shift features."""

import pandas as pd


def shift_process(df: pd.DataFrame, features: list[str], shift: int) -> pd.DataFrame:
    """Process margins between teams."""
    if shift == 0:
        return df
    df[features] = df[features].shift(shift)
    return df
