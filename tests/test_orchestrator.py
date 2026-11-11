import json

import pytest

from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.agents.base import AgentOutputError
from agentforge.demo import DEMO_RESPONSES
from agentforge.llm import StubLLMClient
from agentforge.messages import Task


def _orch(responses) -> tuple[Orchestrator, StubLLMClient]:
    llm = StubLLMClient(responses)
    return Orchestrator(Architect(llm), Developer(llm), QA(llm)), llm


def test_routes_outputs_between_agents() -> None:
    orch, llm = _orch(DEMO_RESPONSES)
    orch.run(Task("add a login page"))
    assert "add a login page" in llm.calls[0][1]
    assert "Add a login page" in llm.calls[1][1]  # architect output reaches developer
    assert "render_login" in llm.calls[2][1]  # developer output reaches QA


def test_records_steps_in_order() -> None:
    orch, _ = _orch(DEMO_RESPONSES)
    result = orch.run(Task("t"))
    assert result.task == Task("t")
    assert result.passed
    assert [s.agent for s in result.steps] == ["architect", "developer", "qa"]


def test_reports_failed_review() -> None:
    failing = (*DEMO_RESPONSES[:2], json.dumps({"passed": False, "issues": ["bad"]}))
    orch, llm = _orch(failing)
    result = orch.run(Task("t"))
    assert not result.passed
    assert len(llm.calls) == 3


def test_propagates_agent_output_error() -> None:
    orch, _ = _orch(["not json"])
    with pytest.raises(AgentOutputError):
        orch.run(Task("t"))
