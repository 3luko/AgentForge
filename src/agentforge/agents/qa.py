"""QA agent: checks code changes against the plan's acceptance criteria."""

from __future__ import annotations

from agentforge.agents.base import Agent
from agentforge.llm import LLMClient
from agentforge.messages import ReviewReport, ReviewRequest


class QA(Agent[ReviewRequest, ReviewReport]):
    """Reviews changes and reports pass/fail with the reasons for any failure."""

    name = "qa"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: ReviewRequest) -> ReviewReport:
        raise NotImplementedError("QA agent is not implemented yet")
