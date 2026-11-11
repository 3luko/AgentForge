# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AgentForge is a learning/portfolio project: a multi-agent pipeline (orchestrator, architect, developer, QA) that turns a feature request into reviewed code. `README.md` has the goal, scope and milestones. `docs/architecture.md` has the module layout and design decisions. The agents are currently stubs that raise `NotImplementedError`.

## Commands

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell; Git Bash: source .venv/Scripts/activate; Linux/macOS: source .venv/bin/activate

python -m pip install -e ".[dev]"

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


## Development workflow (Claude Code subagents)

The `architect`, `developer` and `qa-engineer` subagents in `.claude/agents/` help build this repo. They are not the Python agents in `src/agentforge/`.

**Significant change** = touches `messages.py`, adds a module, changes more than ~3 files, or crosses an agent boundary. For these:

1. `architect` writes a plan. Present it and wait for approval.
2. `developer` implements the approved plan.
3. `qa-engineer` validates it.
4. Summarise changes, test results and open issues.

**Anything smaller** (a single-file fix, tests, docs, renames): do it directly with no subagents.

When delegating, keep tokens down:
- Pass the subagent the approved plan and the exact file paths. Don't make it re-explore the repo.
- Paste only the plan section a subagent needs, not the whole conversation.
- Skip `architect` when the user has already specified the design.
- Don't re-run work a subagent already reported (e.g. re-reading the files it changed) unless something looks wrong.

## Rules

- Change message types in `messages.py` only with explicit approval.
- Add or update tests whenever behaviour changes. Run `pytest` and `ruff check .` before reporting done, and report failures as they are.
- Never read, print or commit secrets (`.env`, API keys).
- Don't commit, push or run destructive commands without approval.
