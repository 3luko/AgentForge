"""Developer agent: writes or changes code to carry out a plan."""

from __future__ import annotations

from agentforge.agents.base import Agent
from agentforge.llm import LLMClient
from agentforge.messages import CodeChange, DesignPlan


class Developer(Agent[DesignPlan, CodeChange]):
    """Produces the file changes that implement a design plan."""

    name = "developer"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: DesignPlan) -> CodeChange:
        raise NotImplementedError("Developer agent is not implemented yet")
