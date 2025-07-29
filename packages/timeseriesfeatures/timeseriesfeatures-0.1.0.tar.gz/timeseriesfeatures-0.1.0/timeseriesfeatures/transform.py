"""Transform enumeration."""

from enum import StrEnum, auto


class Transform(StrEnum):
    """Transform enumeration."""

    NONE = auto()
    VELOCITY = auto()
    LOG = auto()
    ACCELERATION = auto()
    JERK = auto()
    SNAP = auto()
    SMA_5 = auto()
    CRACKLE = auto()
