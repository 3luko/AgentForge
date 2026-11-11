# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AgentForge is a learning/portfolio project: a multi-agent pipeline (orchestrator, architect, developer, QA) that turns a feature request into reviewed code. `README.md` has the goal, scope and milestones. `docs/architecture.md` has the module layout and design decisions. The agents are currently stubs that raise `NotImplementedError`.

## Commands

```bash
python -m venv .venv && .venv/Scripts/activate   # Windows (Git Bash); use .venv/bin/activate elsewhere
pip install -e ".[dev]"

pytest                                    # all tests
pytest tests/agents/test_qa.py            # one file
pytest tests/test_messages.py::test_messages_are_immutable   # one test
ruff check .                              # lint
ruff format .                             # format
agentforge "add a login page"             # run the CLI (or: python -m agentforge.cli "...")
```

## Architecture

- **`src/agentforge/messages.py` is the contract.** Every handoff is a frozen dataclass (`Task → DesignPlan → CodeChange → ReviewRequest → ReviewReport → RunResult`). Add or change message types here first, then the agents.
- **`Agent[InputT, OutputT]`** (`agents/base.py`) has a single `run(message)` method. An agent needing several inputs gets a wrapper message (as with `ReviewRequest`) rather than extra arguments.
- **Only the Orchestrator knows about other agents.** Architect, Developer and QA must import only `base`, `messages` and `llm`. Routing and retry logic belong in `orchestrator.py`.
- **The LLM is injected** through the `LLMClient` protocol (`llm.py`). Tests use `StubLLMClient` (the `stub_llm` fixture in `tests/conftest.py`) with canned responses, so tests never make real API calls.
