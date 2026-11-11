import json

import pytest

from agentforge.agents import Agent, Developer
from agentforge.agents.base import AgentOutputError
from agentforge.llm import StubLLMClient
from agentforge.messages import CodeChange, DesignPlan, DevelopmentRequest, FileChange

PLAN = DesignPlan("build login", ("login.py",), ("renders form",))


def test_developer_is_an_agent(stub_llm) -> None:
    developer = Developer(stub_llm)
    assert isinstance(developer, Agent)
    assert developer.name == "developer"


def test_developer_returns_code_change() -> None:
    body = {"summary": "done", "files": [{"path": "login.py", "content": "x = 1\n"}]}
    developer = Developer(StubLLMClient([json.dumps(body)]))
    assert developer.run(DevelopmentRequest(PLAN)) == CodeChange(
        "done", (FileChange("login.py", "x = 1\n"),)
    )


def test_developer_prompt_contains_plan() -> None:
    llm = StubLLMClient(['{"summary": "d", "files": []}'])
    Developer(llm).run(DevelopmentRequest(PLAN))
    prompt = llm.calls[0][1]
    assert "build login" in prompt
    assert "login.py" in prompt
    assert "renders form" in prompt


def test_developer_rejects_invalid_json() -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient(["nope"])).run(DevelopmentRequest(PLAN))


def test_developer_rejects_file_missing_content() -> None:
    body = {"summary": "d", "files": [{"path": "a.py"}]}
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient([json.dumps(body)])).run(DevelopmentRequest(PLAN))


def test_developer_rejects_missing_files() -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient(['{"summary": "d"}'])).run(DevelopmentRequest(PLAN))


@pytest.mark.parametrize("files", ['"a.py"', '["a.py"]'])
def test_developer_rejects_wrong_typed_files(files: str) -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient([f'{{"summary": "d", "files": {files}}}'])).run(
            DevelopmentRequest(PLAN)
        )


PREVIOUS = CodeChange("first try", (FileChange("login.py", "x = BROKEN\n"),))


def test_developer_prompt_without_previous_has_no_feedback_section() -> None:
    llm = StubLLMClient(['{"summary": "d", "files": []}'])
    Developer(llm).run(DevelopmentRequest(PLAN))
    prompt = llm.calls[0][1]
    assert "Previous attempt" not in prompt
    assert "QA findings" not in prompt


def test_developer_prompt_includes_previous_files_and_findings() -> None:
    llm = StubLLMClient(['{"summary": "d", "files": []}'])
    Developer(llm).run(DevelopmentRequest(PLAN, PREVIOUS, ("missing form", "bad name")))
    prompt = llm.calls[0][1]
    assert "build login" in prompt
    assert "Previous attempt (rejected by QA)" in prompt
    assert "first try" in prompt
    assert "--- login.py ---\nx = BROKEN\n" in prompt
    assert "QA findings to fix:\n- missing form\n- bad name" in prompt
    assert "full corrected contents" in prompt
