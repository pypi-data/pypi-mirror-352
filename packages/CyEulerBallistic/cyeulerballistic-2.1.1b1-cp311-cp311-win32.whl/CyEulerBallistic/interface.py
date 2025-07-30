"""Helper"""
from typing import Optional, Union

from py_ballisticcalc.generics.engine import EngineProtocol

# type: ignore
"""Implements basic interface for the ballistics calculator"""
from dataclasses import dataclass, field

from py_ballisticcalc.interface import Calculator, InterfaceConfigDict


@dataclass
class EulerCalculator(Calculator):
    """Basic interface for the ballistics calculator"""
    _config: Optional[InterfaceConfigDict] = field(default=None)
    _engine: Union[str, EngineProtocol] = field(default='CyEulerBallistic')
    _calc: EngineProtocol = field(init=False, repr=False, compare=False)


__all__ = ('EulerCalculator',)
