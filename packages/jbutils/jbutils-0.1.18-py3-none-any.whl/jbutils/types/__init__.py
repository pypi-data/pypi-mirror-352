"""Common types for the jbutils package"""

from collections.abc import Callable
from typing import TypeVar, Optional, Pattern, Sequence

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
    "TFunction",
    "T",
]
