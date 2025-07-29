"""Common types for the jbutils package"""

from collections.abc import Callable
from typing import TypeVar, Optional


T = TypeVar("T")
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptDict = Optional[dict]
OptList = Optional[list]
Opt = Optional[T]

Predicate = Callable[[T], bool]
Function = Callable[..., None]
TFunction = Callable[..., T]

__all__ = [
    "OptStr",
    "OptInt",
    "OptFloat",
    "OptDict",
    "OptList",
    "Opt",
    "Predicate",
    "Function",
    "TFunction",
    "T",
]
