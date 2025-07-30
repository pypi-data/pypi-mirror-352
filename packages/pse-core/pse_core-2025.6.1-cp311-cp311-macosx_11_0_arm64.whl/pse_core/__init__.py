from importlib import metadata
from typing import TypeAlias

from .pse_core import StateMachine  # type: ignore[attr-defined]

__version__ = metadata.version(__package__ or "")
del metadata

StateId: TypeAlias = int | str
Edge: TypeAlias = tuple[StateMachine, StateId]
StateGraph: TypeAlias = dict[StateId, list[Edge]]

__all__ = ["Edge", "StateGraph", "StateId"]
