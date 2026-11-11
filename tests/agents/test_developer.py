import json

import pytest

from agentforge.agents import Agent, Developer
from agentforge.agents.base import AgentOutputError
from agentforge.llm import StubLLMClient
from agentforge.messages import CodeChange, DesignPlan, FileChange

PLAN = DesignPlan("build login", ("login.py",), ("renders form",))


def test_developer_is_an_agent(stub_llm) -> None:
    developer = Developer(stub_llm)
    assert isinstance(developer, Agent)
    assert developer.name == "developer"


def test_developer_returns_code_change() -> None:
    body = {"summary": "done", "files": [{"path": "login.py", "content": "x = 1\n"}]}
    developer = Developer(StubLLMClient([json.dumps(body)]))
    assert developer.run(PLAN) == CodeChange("done", (FileChange("login.py", "x = 1\n"),))


def test_developer_prompt_contains_plan() -> None:
    llm = StubLLMClient(['{"summary": "d", "files": []}'])
    Developer(llm).run(PLAN)
    prompt = llm.calls[0][1]
    assert "build login" in prompt
    assert "login.py" in prompt
    assert "renders form" in prompt


def test_developer_rejects_invalid_json() -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient(["nope"])).run(PLAN)


def test_developer_rejects_file_missing_content() -> None:
    body = {"summary": "d", "files": [{"path": "a.py"}]}
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient([json.dumps(body)])).run(PLAN)


def test_developer_rejects_missing_files() -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient(['{"summary": "d"}'])).run(PLAN)


@pytest.mark.parametrize("files", ['"a.py"', '["a.py"]'])
def test_developer_rejects_wrong_typed_files(files: str) -> None:
    with pytest.raises(AgentOutputError):
        Developer(StubLLMClient([f'{{"summary": "d", "files": {files}}}'])).run(PLAN)
