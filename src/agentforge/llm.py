"""LLM client interface.

Agents depend only on the `LLMClient` protocol, never on a specific provider.
`StubLLMClient` lets the whole pipeline run in tests without API calls; a real
provider client is planned for milestone v0.2.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class LLMClient(Protocol):
    """Anything that can turn a system prompt and a user prompt into text."""

    def complete(self, system: str, prompt: str) -> str: ...


class StubLLMClient:
    """Returns canned responses in order and records every call it receives."""

    def __init__(self, responses: Iterable[str] = ()) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, prompt: str) -> str:
        self.calls.append((system, prompt))
        if not self._responses:
            raise RuntimeError("StubLLMClient has no responses left")
        return self._responses.pop(0)
