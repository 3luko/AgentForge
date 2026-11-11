from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.messages import Task


def test_pipeline_runs_end_to_end(demo_stub_llm) -> None:
    llm = demo_stub_llm
    orchestrator = Orchestrator(Architect(llm), Developer(llm), QA(llm))
    result = orchestrator.run(Task(description="add a login page"))
    assert result.passed
    assert [step.agent for step in result.steps] == ["architect", "developer", "qa"]
