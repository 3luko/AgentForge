"""Architect agent: turns a feature request into a technical plan."""

from __future__ import annotations

from agentforge.agents.base import Agent
from agentforge.llm import LLMClient
from agentforge.messages import DesignPlan, Task


class Architect(Agent[Task, DesignPlan]):
    """Decides which files to touch, the interfaces involved, and the acceptance criteria."""

    name = "architect"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: Task) -> DesignPlan:
        raise NotImplementedError("Architect agent is not implemented yet")
