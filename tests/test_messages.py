import dataclasses

import pytest

from agentforge.messages import (
    CodeChange,
    DesignPlan,
    DevelopmentRequest,
    ReviewReport,
    RunResult,
    Task,
)


def test_messages_are_immutable() -> None:
    task = Task(description="Add a login page")
    with pytest.raises(dataclasses.FrozenInstanceError):
        task.description = "something else"  # type: ignore[misc]


def test_optional_fields_default_to_empty() -> None:
    plan = DesignPlan(summary="Add a login page")
    assert plan.files_to_change == ()
    assert plan.acceptance_criteria == ()
    assert ReviewReport(passed=True).issues == ()


def test_development_request_defaults_and_immutability() -> None:
    request = DevelopmentRequest(DesignPlan("p"))
    assert request.previous is None
    assert request.findings == ()
    with pytest.raises(dataclasses.FrozenInstanceError):
        request.findings = ("x",)  # type: ignore[misc]


def test_development_request_rejects_findings_without_previous() -> None:
    with pytest.raises(ValueError):
        DevelopmentRequest(DesignPlan("p"), None, ("bad",))


def test_development_request_rejects_previous_without_findings() -> None:
    with pytest.raises(ValueError):
        DevelopmentRequest(DesignPlan("p"), CodeChange("c"), ())


def test_development_request_accepts_valid_retry() -> None:
    request = DevelopmentRequest(DesignPlan("p"), CodeChange("c"), ("bad",))
    assert request.findings == ("bad",)


@pytest.mark.parametrize("findings", [["bad"], ("bad", 1), "bad", None])
def test_development_request_rejects_non_tuple_of_str_findings(findings) -> None:
    with pytest.raises(TypeError):
        DevelopmentRequest(DesignPlan("p"), CodeChange("c"), findings)


def test_development_request_rejects_list_findings_on_initial_request() -> None:
    with pytest.raises(TypeError):
        DevelopmentRequest(DesignPlan("p"), None, [])


def test_run_result_defaults() -> None:
    result = RunResult(Task("t"), True)
    assert result.attempts == 0
    assert result.failure is None
