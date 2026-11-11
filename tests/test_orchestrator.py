import json

import pytest

from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.agents.architect import SYSTEM_PROMPT as ARCHITECT_PROMPT
from agentforge.agents.base import AgentOutputError
from agentforge.demo import DEMO_RESPONSES
from agentforge.llm import StubLLMClient
from agentforge.messages import Task

PLAN = DEMO_RESPONSES[0]


def _dev(content: str) -> str:
    return json.dumps({"summary": "s", "files": [{"path": "login.py", "content": content}]})


def _qa(*issues: str) -> str:
    return json.dumps({"passed": not issues, "issues": list(issues)})


def _script(failures: int, passes: bool = False) -> list[str]:
    """Architect, then `failures` rejected dev/qa rounds, then optionally an approved one."""
    out = [PLAN]
    for i in range(failures):
        out += [_dev(f"CODE{i + 1}"), _qa(f"FINDING{i + 1}")]
    if passes:
        out += [_dev("GOOD"), _qa()]
    return out


def _orch(responses, **kwargs) -> tuple[Orchestrator, StubLLMClient]:
    llm = StubLLMClient(responses)
    return Orchestrator(Architect(llm), Developer(llm), QA(llm), **kwargs), llm


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
    orch, llm = _orch(_script(3))
    result = orch.run(Task("t"))
    assert not result.passed
    assert len(llm.calls) == 7


def test_propagates_agent_output_error() -> None:
    orch, _ = _orch(["not json"])
    with pytest.raises(AgentOutputError):
        orch.run(Task("t"))


def test_approves_first_try() -> None:
    orch, llm = _orch(DEMO_RESPONSES)
    result = orch.run(Task("t"))
    assert result.passed
    assert result.attempts == 1
    assert result.failure is None
    assert [s.agent for s in result.steps] == ["architect", "developer", "qa"]
    assert sum(1 for system, _ in llm.calls if system == ARCHITECT_PROMPT) == 1


def test_stops_immediately_on_approval() -> None:
    orch, llm = _orch([*DEMO_RESPONSES, _dev("spare"), _qa()])
    result = orch.run(Task("t"))
    assert result.attempts == 1
    assert len(llm.calls) == 3


def test_rejects_then_approves() -> None:
    orch, _ = _orch(_script(1, passes=True))
    result = orch.run(Task("t"))
    assert result.passed
    assert result.attempts == 2
    assert len(result.steps) == 5
    assert result.failure is None


def test_exhausted_retries_fail() -> None:
    orch, _ = _orch(_script(3))
    result = orch.run(Task("t"))
    assert not result.passed
    assert result.attempts == 3
    assert result.failure is not None
    assert "3" in result.failure
    assert "FINDING3" in result.failure


def test_three_attempts_produce_seven_steps() -> None:
    orch, _ = _orch(_script(3))
    result = orch.run(Task("t"))
    assert [s.agent for s in result.steps] == [
        "architect",
        "developer",
        "qa",
        "developer",
        "qa",
        "developer",
        "qa",
    ]


def test_retry_prompt_carries_previous_code_and_findings() -> None:
    orch, llm = _orch(_script(1, passes=True))
    orch.run(Task("t"))
    first = llm.calls[1][1]
    retry = llm.calls[3][1]
    assert "CODE1" not in first and "FINDING1" not in first
    assert "CODE1" in retry and "FINDING1" in retry


def test_only_latest_attempt_is_carried_forward() -> None:
    orch, llm = _orch(_script(3))
    orch.run(Task("t"))
    third = llm.calls[5][1]
    assert "CODE2" in third and "FINDING2" in third
    assert "CODE1" not in third and "FINDING1" not in third


def test_architect_runs_once_across_retries() -> None:
    orch, llm = _orch(_script(3))
    orch.run(Task("t"))
    assert sum(1 for system, _ in llm.calls if system == ARCHITECT_PROMPT) == 1


@pytest.mark.parametrize(
    ("plan", "field"),
    [
        ({"summary": "s", "files_to_change": [], "acceptance_criteria": ["c"]}, "files_to_change"),
        (
            {"summary": "s", "files_to_change": ["a.py"], "acceptance_criteria": []},
            "acceptance_criteria",
        ),
    ],
)
def test_unready_plan_skips_developer(plan, field) -> None:
    orch, llm = _orch([json.dumps(plan), _dev("x"), _qa()])
    result = orch.run(Task("t"))
    assert not result.passed
    assert result.attempts == 0
    assert result.failure is not None and field in result.failure
    assert [s.agent for s in result.steps] == ["architect"]
    assert len(llm.calls) == 1


def test_unready_plan_reports_both_missing_fields() -> None:
    plan = {"summary": "s", "files_to_change": [], "acceptance_criteria": []}
    orch, llm = _orch([json.dumps(plan), _dev("x"), _qa()])
    result = orch.run(Task("t"))
    assert not result.passed
    assert result.attempts == 0
    assert result.failure is not None
    assert "files_to_change" in result.failure
    assert "acceptance_criteria" in result.failure
    assert [s.agent for s in result.steps] == ["architect"]
    assert len(llm.calls) == 1


@pytest.mark.parametrize(("max_retries", "attempts"), [(0, 1), (1, 2), (4, 5)])
def test_max_retries_bounds_attempts(max_retries: int, attempts: int) -> None:
    orch, _ = _orch(_script(5), max_retries=max_retries)
    result = orch.run(Task("t"))
    assert not result.passed
    assert result.attempts == attempts


def test_max_retries_zero_passes_on_first_attempt() -> None:
    orch, llm = _orch(_script(0, passes=True), max_retries=0)
    result = orch.run(Task("t"))
    assert result.passed
    assert result.attempts == 1
    assert result.failure is None
    assert len(llm.calls) == 3


def test_max_retries_above_two_allows_late_approval() -> None:
    orch, llm = _orch(_script(4, passes=True), max_retries=4)
    result = orch.run(Task("t"))
    assert result.passed
    assert result.attempts == 5
    assert len(result.steps) == 11
    assert len(llm.calls) == 11


def test_negative_max_retries_rejected() -> None:
    llm = StubLLMClient()
    with pytest.raises(ValueError):
        Orchestrator(Architect(llm), Developer(llm), QA(llm), max_retries=-1)


def test_output_error_on_retry_propagates() -> None:
    orch, _ = _orch([*_script(1), "not json"])
    with pytest.raises(AgentOutputError):
        orch.run(Task("t"))
