"""Compute NBEATS features."""

import os

import pandas as pd
from sktime.forecasting import model_selection  # type: ignore
from sktime.forecasting import pytorchforecasting
from sktime.forecasting.base import ForecastingHorizon  # type: ignore

from .cache import CACHE_FOLDER
from .feature import FEATURE_TYPE_NBEATS, Feature
from .transform import Transform

NBEATS_MODEL_EXT = "pkl"
DT_SANITISATION_REPLACEMENTS = {
    ":": "_",
    "/": "-",
}
NBEATS_MODEL_PREFIX = "nbeats_"
NBEATS_FOLDER_PREFIX = "nbeats"


def sanitise_dt_isoformat(column: str) -> str:
    """Sanitise a datetime ISO format."""
    for k, v in DT_SANITISATION_REPLACEMENTS.items():
        column = column.replace(k, v)
    return column


def compute_nbeats(series: pd.Series, max_lag: int, min_lag: int) -> list[Feature]:
    """Compute nbeats features."""
    model_name = "_".join(
        [NBEATS_FOLDER_PREFIX, str(series.name), str(max_lag), str(min_lag)]
    )
    model_folder = os.path.join(CACHE_FOLDER, model_name)
    os.makedirs(model_folder, exist_ok=True)
    splitter = model_selection.SlidingWindowSplitter(
        window_length=365, fh=min_lag, step_length=7, start_with_window=True
    )
    for train_idx, test_idx in splitter.split(series):
        y_train = series.iloc[train_idx]
        target_time = series.index[
            test_idx[0]
        ]  # forecast time index (e.g., Timestamp or int)
        fh = ForecastingHorizon(range(1, min_lag + 1), is_relative=True)
        target_label = sanitise_dt_isoformat(str(target_time))
        model_path = os.path.join(model_folder, f"{NBEATS_MODEL_PREFIX}{target_label}")
        if os.path.exists(model_path + ".zip"):
            continue

        model = pytorchforecasting.PytorchForecastingNBeats(
            trainer_params={"max_epochs": 10, "limit_train_batches": 20},
        )
        if len(y_train) < (max_lag + min_lag):
            continue
        model.fit(y=y_train, fh=fh)
        model.save(model_path, serialization_format="cloudpickle")
    return [
        Feature(
            feature_type=FEATURE_TYPE_NBEATS,
            columns=[str(series.name)],
            value1=model_name,
            value2=min_lag,
            transform=str(Transform.NONE),
        )
    ]
