import pytest

from agentforge.demo import demo_llm
from agentforge.llm import StubLLMClient


@pytest.fixture
def stub_llm() -> StubLLMClient:
    """A strict stub with no responses; tests queue their own."""
    return StubLLMClient()


@pytest.fixture
def demo_stub_llm() -> StubLLMClient:
    return demo_llm()
