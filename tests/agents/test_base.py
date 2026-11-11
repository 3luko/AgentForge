import pytest

from agentforge.agents.base import AgentOutputError, parse_json_object


def test_parse_json_object_strips_code_fence() -> None:
    assert parse_json_object("a", '```json\n{"k": 1}\n```') == {"k": 1}
    assert parse_json_object("a", '```\n{"k": 2}\n```') == {"k": 2}


def test_parse_json_object_rejects_non_object() -> None:
    with pytest.raises(AgentOutputError):
        parse_json_object("a", "[1, 2]")
