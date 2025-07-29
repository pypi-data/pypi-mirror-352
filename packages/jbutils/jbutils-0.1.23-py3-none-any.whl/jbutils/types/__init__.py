"""Common types for the jbutils package"""

from collections.abc import Callable
from typing import TypeVar, Optional, Pattern, Sequence, Literal

# General Typing
T = TypeVar("T")
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptDict = Optional[dict]
OptList = Optional[list]
Opt = Optional[T]

# Function Types
Predicate = Callable[[T], bool]
Function = Callable[..., None]
TFunction = Callable[..., T]

# Other
Patterns = Sequence[str | Pattern[str]]
DataPathList = list[str] | list[str | int] | list[int]
DataPath = DataPathList | str | int

SubReturn = Literal["out", "err", "both"]
""" String literal type representing the output choices for cmdx """

__all__ = [
    "OptStr",
    "OptInt",
    "OptFloat",
    "OptDict",
    "OptList",
    "Opt",
    "Patterns",
    "Predicate",
    "Function",
    "SubReturn",
    "TFunction",
    "T",
]
