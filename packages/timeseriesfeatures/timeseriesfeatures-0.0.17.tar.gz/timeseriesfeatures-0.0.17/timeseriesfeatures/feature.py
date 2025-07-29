"""The base class for a feature."""

from typing import NotRequired, TypedDict

FEATURE_TYPE_LAG = "lag"
FEATURE_TYPE_ROLLING = "rolling"

VALUE_TYPE_INT = "int"
VALUE_TYPE_DAYS = "days"
VALUE_TYPE_NONE = "none"


class Feature(TypedDict):
    """A description of a feature to use."""

    feature_type: str
    columns: list[str]
    value1: str | int | None
    value2: NotRequired[str | int | None]
    transform: str
    rank_value: NotRequired[float]
    rank_type: NotRequired[str]
