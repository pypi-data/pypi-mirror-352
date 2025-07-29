"""A list of transforms."""

from .transform import Transform
from .transform_derivative import create_derivative_transform
from .transform_log import log_transform
from .transform_sma import create_sma_transform

TRANSFORMS = {
    str(Transform.NONE): lambda x: x,
    str(Transform.VELOCITY): create_derivative_transform(1),
    str(Transform.LOG): log_transform,
    str(Transform.ACCELERATION): create_derivative_transform(2),
    str(Transform.JERK): create_derivative_transform(3),
    str(Transform.SNAP): create_derivative_transform(4),
    str(Transform.SMA_5): create_sma_transform(5),
    str(Transform.CRACKLE): create_derivative_transform(5),
}
