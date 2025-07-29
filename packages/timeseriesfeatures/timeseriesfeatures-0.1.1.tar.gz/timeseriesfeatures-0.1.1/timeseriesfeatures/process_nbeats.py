"""Process the NBEATS features."""

# pylint: disable=line-too-long
import datetime
import os
from collections import defaultdict

import pandas as pd
from sktime.forecasting import pytorchforecasting  # type: ignore
from sktime.forecasting.base import ForecastingHorizon  # type: ignore

from .cache import CACHE_FOLDER
from .columns import DELIMITER
from .compute_nbeats import DT_SANITISATION_REPLACEMENTS, NBEATS_MODEL_PREFIX
from .feature import FEATURE_TYPE_NBEATS, Feature


def _desanitise_dt_isoformat(dt: str) -> str:
    for k, v in DT_SANITISATION_REPLACEMENTS.items():
        dt = dt.replace(v, k)
    return dt


def load_model_index(model_dir: str) -> list[tuple[datetime.datetime, str]]:
    """
    Loads the available model timestamps from filenames.
    Assumes files are named like: nbeats_<timestamp>.pkl
    Returns sorted list of (timestamp, path).
    """
    model_files = os.listdir(model_dir)
    models = []
    for file in model_files:
        if not file.endswith(".zip"):
            continue
        name = file.replace(NBEATS_MODEL_PREFIX, "").replace(".zip", "")
        idx = pd.to_datetime(_desanitise_dt_isoformat(name))
        models.append((idx, os.path.join(model_dir, file)))
    return sorted(models, key=lambda x: x[0])


def find_closest_model(
    target_time: datetime.datetime, model_index: list[tuple[datetime.datetime, str]]
):
    """
    Given a list of (timestamp, path), find the latest timestamp <= target_time
    """
    candidates = [m for m in model_index if m[0] <= target_time]
    if not candidates:
        return None
    return candidates[-1][1]  # path of closest earlier model


def _predict_nbeats(series: pd.Series, model_dir: str, min_lag: int) -> pd.Series:
    model_index = load_model_index(model_dir)  # List of (timestamp, path)
    preds = pd.Series(index=series.index, dtype=float)

    # Sort series index so we can batch up by model
    sorted_index = sorted(series.index)
    model_index = sorted(model_index, key=lambda x: x[0])  # sort by model datetime

    # Map each time t to the closest model available before it
    model_to_times = defaultdict(list)

    for t in sorted_index:
        model_path = find_closest_model(t, model_index)
        if model_path is not None:
            model_to_times[model_path].append(t)

    # Predict in batches per model
    for model_path, times in model_to_times.items():
        model = pytorchforecasting.PytorchForecastingNBeats.load_from_path(model_path)

        # This model was trained for a specific forecast time: recover fh from filename or store separately
        # We must re-use the same fh as during training!
        # So: load the .fh file or infer the relative index from training time to prediction time

        # For now, we assume this model was trained with:
        # fh = ForecastingHorizon(range(1, min_lag+1), is_relative=True)
        fh = ForecastingHorizon(range(1, min_lag + 1), is_relative=True)

        pred = model.predict(fh=fh)
        # Fill all requested times with the 1st step-ahead prediction
        for t in times:
            preds.loc[t] = pred.values[0]

    return preds


def process_nbeats(
    df: pd.DataFrame, features: list[Feature], columns: list[str]
) -> pd.DataFrame:
    """Process NBEATS forecasting predictions."""
    if not features:
        return df
    for column in columns:
        for feature in features:
            if feature["feature_type"] != FEATURE_TYPE_NBEATS:
                continue
            if feature["columns"] and column not in feature["columns"]:
                continue
            model_name = feature["value1"]
            if not isinstance(model_name, str):
                continue
            min_lag = feature.get("value2")
            if not isinstance(min_lag, int):
                continue
            df[DELIMITER.join([column, model_name])] = _predict_nbeats(
                df[column], os.path.join(CACHE_FOLDER, model_name), min_lag
            )
    return df
