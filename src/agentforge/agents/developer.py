"""Developer agent: writes or changes code to carry out a plan."""

from __future__ import annotations

from agentforge.agents.base import (
    Agent,
    AgentOutputError,
    parse_json_object,
    require_str,
)
from agentforge.llm import LLMClient
from agentforge.messages import CodeChange, DevelopmentRequest, FileChange

SYSTEM_PROMPT = (
    "You are a software developer. Respond with only a JSON object of the form "
    '{"summary": str, "files": [{"path": str, "content": str}]} where each file '
    "holds the full new contents."
)


class Developer(Agent[DevelopmentRequest, CodeChange]):
    """Produces the file changes that implement a design plan."""

    name = "developer"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, message: DevelopmentRequest) -> CodeChange:
        plan = message.plan
        files = "\n".join(f"- {f}" for f in plan.files_to_change)
        criteria = "\n".join(f"- {c}" for c in plan.acceptance_criteria)
        prompt = (
            f"Plan: {plan.summary}\n\nFiles to change:\n{files}\n\nAcceptance criteria:\n{criteria}"
        )
        if message.previous is not None:
            previous_files = "\n\n".join(
                f"--- {f.path} ---\n{f.content}" for f in message.previous.files
            )
            findings = "\n".join(f"- {issue}" for issue in message.findings)
            prompt += (
                "\n\nPrevious attempt (rejected by QA):\n"
                f"{message.previous.summary}\n\n{previous_files}"
                f"\n\nQA findings to fix:\n{findings}"
                "\n\nReturn the full corrected contents of every file."
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
