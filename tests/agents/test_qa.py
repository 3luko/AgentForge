import pytest

from agentforge.agents import QA, Agent
from agentforge.agents.base import AgentOutputError
from agentforge.llm import StubLLMClient
from agentforge.messages import CodeChange, DesignPlan, FileChange, ReviewRequest

REQUEST = ReviewRequest(
    DesignPlan("p", ("a.py",), ("must render",)),
    CodeChange("c", (FileChange("a.py", "print('hi')"),)),
)


def test_qa_is_an_agent(stub_llm) -> None:
    qa = QA(stub_llm)
    assert isinstance(qa, Agent)
    assert qa.name == "qa"


def test_qa_returns_passing_report() -> None:
    report = QA(StubLLMClient(['{"passed": true, "issues": []}'])).run(REQUEST)
    assert report.passed
    assert report.issues == ()


def test_qa_returns_failing_report_with_issues() -> None:
    report = QA(StubLLMClient(['{"passed": false, "issues": ["bad", "worse"]}'])).run(REQUEST)
    assert not report.passed
    assert report.issues == ("bad", "worse")


def test_qa_prompt_contains_criteria_and_file_content() -> None:
    llm = StubLLMClient(['{"passed": true}'])
    QA(llm).run(REQUEST)
    prompt = llm.calls[0][1]
    assert "must render" in prompt
    assert "a.py" in prompt
    assert "print('hi')" in prompt


def test_qa_rejects_non_bool_passed() -> None:
    with pytest.raises(AgentOutputError):
        QA(StubLLMClient(['{"passed": "true"}'])).run(REQUEST)


def test_qa_rejects_invalid_json() -> None:
    with pytest.raises(AgentOutputError):
        QA(StubLLMClient(["nope"])).run(REQUEST)


def test_qa_rejects_failed_review_without_issues() -> None:
    with pytest.raises(AgentOutputError):
        QA(StubLLMClient(['{"passed": false, "issues": []}'])).run(REQUEST)


def test_qa_rejects_wrong_typed_issues() -> None:
    with pytest.raises(AgentOutputError):
        QA(StubLLMClient(['{"passed": false, "issues": "bad"}'])).run(REQUEST)
