"""Base class shared by every agent."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

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


class AgentOutputError(ValueError):
    """An agent's LLM response could not be turned into its output message."""

    def __init__(self, agent_name: str, detail: str) -> None:
        super().__init__(f"{agent_name}: {detail}")
        self.agent_name = agent_name
        self.detail = detail


_FENCE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```$", re.DOTALL | re.IGNORECASE)


def parse_json_object(agent_name: str, text: str) -> dict[str, Any]:
    """Parse an LLM response as a JSON object, tolerating a Markdown code fence."""
    cleaned = text.strip()
    match = _FENCE.match(cleaned)
    if match:
        cleaned = match.group(1).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AgentOutputError(agent_name, f"response is not valid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise AgentOutputError(agent_name, "response must be a JSON object")
    return data


def require_str(agent_name: str, data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise AgentOutputError(agent_name, f"'{key}' must be a string")
    return value


def str_list(agent_name: str, data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise AgentOutputError(agent_name, f"'{key}' must be a list of strings")
    return tuple(value)
