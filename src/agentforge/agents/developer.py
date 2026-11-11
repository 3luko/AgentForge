"""Developer agent: writes or changes code to carry out a plan."""

from __future__ import annotations

from agentforge.agents.base import (
    Agent,
    AgentOutputError,
    parse_json_object,
    require_str,
)
from agentforge.llm import LLMClient
from agentforge.messages import CodeChange, DesignPlan, FileChange

SYSTEM_PROMPT = (
    "You are a software developer. Respond with only a JSON object of the form "
    '{"summary": str, "files": [{"path": str, "content": str}]} where each file '
    "holds the full new contents."
)


class Developer(Agent[DesignPlan, CodeChange]):
    """Produces the file changes that implement a design plan."""

    name = "developer"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: DesignPlan) -> CodeChange:
        files = "\n".join(f"- {f}" for f in message.files_to_change)
        criteria = "\n".join(f"- {c}" for c in message.acceptance_criteria)
        prompt = (
            f"Plan: {message.summary}\n\n"
            f"Files to change:\n{files}\n\n"
            f"Acceptance criteria:\n{criteria}"
        )
        data = parse_json_object(self.name, self.llm.complete(SYSTEM_PROMPT, prompt))
        raw_files = data.get("files")
        if not isinstance(raw_files, list):
            raise AgentOutputError(self.name, "'files' is required and must be a list")
        changes = []
        for item in raw_files:
            if not isinstance(item, dict):
                raise AgentOutputError(self.name, "each file must be an object")
            changes.append(
                FileChange(
                    path=require_str(self.name, item, "path"),
                    content=require_str(self.name, item, "content"),
                )
            )
        return CodeChange(summary=require_str(self.name, data, "summary"), files=tuple(changes))
