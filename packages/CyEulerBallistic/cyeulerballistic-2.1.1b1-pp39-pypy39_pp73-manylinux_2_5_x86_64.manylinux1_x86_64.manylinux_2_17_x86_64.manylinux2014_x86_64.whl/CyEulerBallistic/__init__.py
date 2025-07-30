# type: ignore
__author__ = "o-murphy"
__copyright__ = (
    "Copyright 2023 Dmytro Yaroshenko (https://github.com/o-murphy)",
    "Copyright 2024 David Bookstaber (https://github.com/dbookstaber)"
)

__credits__ = ["o-murphy", "dbookstaber"]

from .trajectory_calc import EulerTrajectoryCalc
from .vector import Vector
from .trajectory_data import TrajectoryData
from .interface import EulerCalculator

__all__ = (
    'EulerTrajectoryCalc',
    'Vector',
    'TrajectoryData',
    'EulerCalculator'
)
