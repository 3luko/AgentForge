import dataclasses

import pytest

from agentforge.messages import DesignPlan, ReviewReport, Task


def test_messages_are_immutable() -> None:
    task = Task(description="Add a login page")
    with pytest.raises(dataclasses.FrozenInstanceError):
        task.description = "something else"  # type: ignore[misc]


def test_optional_fields_default_to_empty() -> None:
    plan = DesignPlan(summary="Add a login page")
    assert plan.files_to_change == ()
    assert plan.acceptance_criteria == ()
    assert ReviewReport(passed=True).issues == ()
