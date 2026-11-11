"""Base class shared by every agent."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class Agent(ABC, Generic[InputT, OutputT]):
    """An agent consumes one message type and produces another.

    Subclasses declare their input and output types, e.g.
    `class Architect(Agent[Task, DesignPlan])`, which makes each handoff in the
    pipeline explicit and type-checkable.
    """

    name: str = "agent"

    @abstractmethod
    def run(self, message: InputT) -> OutputT:
        """Process one input message and return the output message."""
