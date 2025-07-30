# type: ignore
from typing_extensions import NamedTuple, Union, Tuple

from py_ballisticcalc.unit import Angular, Distance, Energy, Velocity, Weight, Vector

__all__ = ['TrajectoryData']


class BaseTrajData(NamedTuple):
    """Minimal data for one point in ballistic trajectory"""
    time: float
    position: Vector
    velocity: Vector
    mach: float


class TrajectoryData(NamedTuple):
    __slots__: Tuple[str, ...]
    _field: Tuple[str, ...]

    time: float
    distance: Distance
    velocity: Velocity
    mach: float
    height: Distance
    target_drop: Distance
    drop_adj: Angular
    windage: Distance
    windage_adj: Angular
    look_distance: Distance
    angle: Angular
    density_factor: float
    drag: float
    energy: Energy
    ogw: Weight
    flag: Union[int]

    def formatted(self) -> tuple[str, ...]: ...

    def in_def_units(self) -> tuple[float, ...]: ...
