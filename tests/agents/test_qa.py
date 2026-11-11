from agentforge.agents import QA, Agent


def test_qa_is_an_agent(stub_llm) -> None:
    qa = QA(stub_llm)
    assert isinstance(qa, Agent)
    assert qa.name == "qa"
