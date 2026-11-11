import pytest

from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.messages import Task


@pytest.mark.skip(reason="agents are not implemented yet (milestone v0.1)")
def test_pipeline_runs_end_to_end(stub_llm) -> None:
    orchestrator = Orchestrator(Architect(stub_llm), Developer(stub_llm), QA(stub_llm))
    result = orchestrator.run(Task(description="Add a hello-world endpoint"))
    assert result.passed
    assert [step.agent for step in result.steps] == ["architect", "developer", "qa"]
