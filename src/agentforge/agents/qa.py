"""QA agent: checks code changes against the plan's acceptance criteria."""

from __future__ import annotations

from agentforge.agents.base import Agent, AgentOutputError, parse_json_object, str_list
from agentforge.llm import LLMClient
from agentforge.messages import ReviewReport, ReviewRequest

SYSTEM_PROMPT = (
    "You are a QA engineer. Review the changes against the acceptance criteria. "
    'Respond with only a JSON object of the form {"passed": bool, "issues": [str]}.'
)


class QA(Agent[ReviewRequest, ReviewReport]):
    """Reviews changes and reports pass/fail with the reasons for any failure."""

    name = "qa"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: ReviewRequest) -> ReviewReport:
        criteria = "\n".join(f"- {c}" for c in message.plan.acceptance_criteria)
        files = "\n\n".join(f"--- {f.path} ---\n{f.content}" for f in message.changes.files)
        prompt = f"Acceptance criteria:\n{criteria}\n\nChanged files:\n{files}"
        data = parse_json_object(self.name, self.llm.complete(SYSTEM_PROMPT, prompt))
        passed = data.get("passed")
        if not isinstance(passed, bool):
            raise AgentOutputError(self.name, "'passed' must be a boolean")
        issues = str_list(self.name, data, "issues")
        if not passed and not issues:
            raise AgentOutputError(self.name, "a failed review must list at least one issue")
        return ReviewReport(passed=passed, issues=issues)
