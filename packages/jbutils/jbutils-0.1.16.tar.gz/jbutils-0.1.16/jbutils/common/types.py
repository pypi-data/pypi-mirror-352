"""Common types defined for the jbutils package"""

from collections.abc import Callable
from typing import TypeVar, Optional

T = TypeVar("T")

Predicate = Callable[[T], bool]

OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptDict = Optional[dict]
OptList = Optional[list]
Opt = Optional[T]
