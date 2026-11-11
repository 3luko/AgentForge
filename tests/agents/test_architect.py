from agentforge.agents import Agent, Architect


def test_architect_is_an_agent(stub_llm) -> None:
    architect = Architect(stub_llm)
    assert isinstance(architect, Agent)
    assert architect.name == "architect"
