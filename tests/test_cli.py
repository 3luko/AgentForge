import json

from agentforge.cli import main
from agentforge.demo import DEMO_RESPONSES
from agentforge.llm import StubLLMClient


def test_prints_result_and_step_log(capsys) -> None:
    assert main(["add a login page"]) == 0
    out = capsys.readouterr().out
    assert "PASSED" in out
    assert "Attempts: 1" in out
    assert "Failure" not in out
    for name in ("architect", "developer", "qa"):
        assert name in out


def test_reports_agent_output_error(capsys) -> None:
    assert main(["x"], llm=StubLLMClient(["not json"])) == 1
    assert "architect" in capsys.readouterr().err


def test_prints_failed_result_with_issues(capsys) -> None:
    fail = json.dumps({"passed": False, "issues": ["no form"]})
    responses = (*DEMO_RESPONSES[:2], fail, DEMO_RESPONSES[1], fail, DEMO_RESPONSES[1], fail)
    assert main(["x"], llm=StubLLMClient(responses)) == 0
    out = capsys.readouterr().out
    assert "Result: FAILED" in out
    assert "Attempts: 3" in out
    assert "Failure: QA rejected 3 attempt(s); last findings: no form" in out
    assert "3. qa: failed - no form" in out
    out.encode("ascii")  # plain ASCII, safe on any Windows console code page


def test_notes_stub_llm_on_stderr(capsys) -> None:
    main(["x"])
    assert "stub LLM" in capsys.readouterr().err
