"""Orchestrator agent: owns the task lifecycle and routes work between agents."""

from __future__ import annotations

from agentforge.agents.architect import Architect
from agentforge.agents.base import Agent
from agentforge.agents.developer import Developer
from agentforge.agents.qa import QA
from agentforge.messages import RunResult, Task


class Orchestrator(Agent[Task, RunResult]):
    """Runs Architect -> Developer -> QA and records each step.

    This is the only agent that knows about the others, so all routing and
    (from v0.3) retry logic lives here.
    """

    name = "orchestrator"

    def __init__(self, architect: Architect, developer: Developer, qa: QA) -> None:
        self.architect = architect
        self.developer = developer
        self.qa = qa

    def run(self, message: Task) -> RunResult:
        raise NotImplementedError("Orchestrator agent is not implemented yet")
