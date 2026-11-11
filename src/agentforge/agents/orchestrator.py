"""Orchestrator agent: owns the task lifecycle and routes work between agents."""

from __future__ import annotations

from agentforge.agents.architect import Architect
from agentforge.agents.base import Agent
from agentforge.agents.developer import Developer
from agentforge.agents.qa import QA
from agentforge.messages import (
    DesignPlan,
    DevelopmentRequest,
    ReviewRequest,
    RunResult,
    StepRecord,
    Task,
)


def _plan_problems(plan: DesignPlan) -> tuple[str, ...]:
    """Return the reasons a plan can't be handed to the Developer (empty if ready)."""
    problems = []
    if not plan.files_to_change:
        problems.append("files_to_change is empty")
    if not plan.acceptance_criteria:
        problems.append("acceptance_criteria is empty")
    return tuple(problems)


class Orchestrator(Agent[Task, RunResult]):
    """Runs Architect -> Developer -> QA, retrying the Developer on QA rejection.

    This is the only agent that knows about the others, so all routing and
    retry logic lives here. A rejected change is sent back to the Developer
    with the QA findings, at most `max_retries` times. Only the latest change
    and its findings are carried forward. Malformed agent output is not
    retried; AgentOutputError propagates.
    """

    name = "orchestrator"

    def __init__(
        self, architect: Architect, developer: Developer, qa: QA, max_retries: int = 2
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.architect = architect
        self.developer = developer
        self.qa = qa
        self.max_retries = max_retries

    def run(self, message: Task) -> RunResult:
        plan = self.architect.run(message)
        steps = [StepRecord(self.architect.name, plan)]
        problems = _plan_problems(plan)
        if problems:
            return RunResult(
                message,
                False,
                tuple(steps),
                attempts=0,
                failure="plan not ready: " + "; ".join(problems),
            )

        previous = None
        findings: tuple[str, ...] = ()
        max_attempts = 1 + self.max_retries
        for attempt in range(1, max_attempts + 1):
            change = self.developer.run(DevelopmentRequest(plan, previous, findings))
            steps.append(StepRecord(self.developer.name, change))
            report = self.qa.run(ReviewRequest(plan=plan, changes=change))
            steps.append(StepRecord(self.qa.name, report))
            if report.passed:
                return RunResult(message, True, tuple(steps), attempts=attempt, failure=None)
            previous, findings = change, report.issues
        return RunResult(
            message,
            False,
            tuple(steps),
            attempts=max_attempts,
            failure=f"QA rejected {max_attempts} attempt(s); last findings: " + "; ".join(findings),
        )
