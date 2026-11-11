"""Canned LLM responses so the CLI can run the pipeline without a real provider."""

from __future__ import annotations

import json

from agentforge.llm import StubLLMClient

DEMO_RESPONSES: tuple[str, ...] = (
    json.dumps(
        {
            "summary": "Add a login page",
            "files_to_change": ["login.py"],
            "acceptance_criteria": ["A login page can be rendered"],
        }
    ),
    json.dumps(
        {
            "summary": "Implement a minimal login page",
            "files": [
                {
                    "path": "login.py",
                    "content": "def render_login() -> str:\n    return '<form>login</form>'\n",
                }
            ],
        }
    ),
    json.dumps({"passed": True, "issues": []}),
)


def demo_llm() -> StubLLMClient:
    """Return a fresh stub primed with the demo responses."""
    return StubLLMClient(DEMO_RESPONSES)
