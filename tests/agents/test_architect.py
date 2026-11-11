import json

import pytest

from agentforge.agents import Agent, Architect
from agentforge.agents.base import AgentOutputError
from agentforge.llm import StubLLMClient
from agentforge.messages import DesignPlan, Task


def _arch(response: str) -> tuple[Architect, StubLLMClient]:
    llm = StubLLMClient([response])
    return Architect(llm), llm


def test_architect_is_an_agent(stub_llm) -> None:
    architect = Architect(stub_llm)
    assert isinstance(architect, Agent)
    assert architect.name == "architect"


def test_architect_returns_design_plan() -> None:
    body = {"summary": "s", "files_to_change": ["a.py"], "acceptance_criteria": ["c"]}
    architect, _ = _arch(json.dumps(body))
    assert architect.run(Task("x")) == DesignPlan("s", ("a.py",), ("c",))


def test_architect_prompt_contains_task_description() -> None:
    architect, llm = _arch('{"summary": "s"}')
    architect.run(Task("add a login page"))
    assert "Feature request: add a login page" in llm.calls[0][1]


def test_architect_defaults_missing_lists_to_empty() -> None:
    architect, _ = _arch('{"summary": "s"}')
    plan = architect.run(Task("x"))
    assert plan.files_to_change == ()
    assert plan.acceptance_criteria == ()


def test_architect_rejects_invalid_json() -> None:
    architect, _ = _arch("not json")
    with pytest.raises(AgentOutputError):
        architect.run(Task("x"))


def test_architect_rejects_missing_summary() -> None:
    architect, _ = _arch("{}")
    with pytest.raises(AgentOutputError):
        architect.run(Task("x"))


def test_architect_accepts_fenced_json() -> None:
    architect, _ = _arch('```json\n{"summary": "s"}\n```')
    assert architect.run(Task("x")).summary == "s"


@pytest.mark.parametrize("key", ["files_to_change", "acceptance_criteria"])
def test_architect_rejects_wrong_typed_lists(key: str) -> None:
    body = {"summary": "s", key: "not a list"}
    with pytest.raises(AgentOutputError):
        Architect(StubLLMClient([json.dumps(body)])).run(Task("t"))
