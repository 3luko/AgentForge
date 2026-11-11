"""Architect agent: turns a feature request into a technical plan."""

from __future__ import annotations

from typing import Any

from agentforge.agents.base import (
    Agent,
    AgentOutputError,
    parse_json_object,
    require_str,
    str_list,
)
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
        summary = require_str(self.name, data, "summary")
        if not summary.strip():
            raise AgentOutputError(self.name, "'summary' must not be blank")
        return DesignPlan(
            summary=summary,
            files_to_change=self._entries(data, "files_to_change"),
            acceptance_criteria=self._entries(data, "acceptance_criteria"),
        )

    def _entries(self, data: dict[str, Any], key: str) -> tuple[str, ...]:
        """A list field with no blank or duplicate entries; omitted means empty."""
        entries = str_list(self.name, data, key)
        if any(not entry.strip() for entry in entries):
            raise AgentOutputError(self.name, f"'{key}' must not contain blank entries")
        if len(set(entries)) != len(entries):
            raise AgentOutputError(self.name, f"'{key}' must not contain duplicate entries")
        return entries
