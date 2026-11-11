from agentforge.agents import Agent, Developer


def test_developer_is_an_agent(stub_llm) -> None:
    developer = Developer(stub_llm)
    assert isinstance(developer, Agent)
    assert developer.name == "developer"
