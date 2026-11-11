"""Architect agent: turns a feature request into a technical plan."""

from __future__ import annotations

from agentforge.agents.base import Agent, parse_json_object, require_str, str_list
from agentforge.llm import LLMClient
from agentforge.messages import DesignPlan, Task

SYSTEM_PROMPT = (
    "You are a software architect. Respond with only a JSON object of the form "
    '{"summary": str, "files_to_change": [str], "acceptance_criteria": [str]}.'
)


class Architect(Agent[Task, DesignPlan]):
    """Decides which files to touch, the interfaces involved, and the acceptance criteria."""

    name = "architect"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: Task) -> DesignPlan:
        text = self.llm.complete(SYSTEM_PROMPT, f"Feature request: {message.description}")
        data = parse_json_object(self.name, text)
        return DesignPlan(
            summary=require_str(self.name, data, "summary"),
            files_to_change=str_list(self.name, data, "files_to_change"),
            acceptance_criteria=str_list(self.name, data, "acceptance_criteria"),
        )
