import pytest

from agentforge.llm import StubLLMClient


@pytest.fixture
def stub_llm() -> StubLLMClient:
    return StubLLMClient()
