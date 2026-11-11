# Architecture

This document describes how the code is organised. See the [README](../README.md) for the project goal and milestones.

## Pipeline

```
Task ──► Orchestrator
            │
            ├─► Architect   Task           ─► DesignPlan
            ├─► Developer   DesignPlan     ─► CodeChange
            └─► QA          ReviewRequest  ─► ReviewReport
            │               (plan + changes)
            ▼
         RunResult (passed + StepRecord log)
```

## Modules

| Module | Role |
|---|---|
| `agentforge/messages.py` | Frozen dataclasses for every handoff. This is the contract between agents. |
| `agentforge/agents/base.py` | `Agent[InputT, OutputT]`, an abstract base with a single `run(message)` method. |
| `agentforge/agents/*.py` | One agent per file. Each declares its input and output message types. |
| `agentforge/llm.py` | The `LLMClient` protocol and `StubLLMClient` for tests. |
| `agentforge/demo.py` | Canned stub responses the CLI uses until a real LLM is connected (v0.2). |
| `agentforge/cli.py` | Wires the agents together and runs a task from the command line. |

## Design decisions

- **Agents depend on messages, not on each other.** Architect, Developer and QA import only `base`, `messages` and `llm`. The Orchestrator is the single place that knows about the other agents, so routing and retry policy stay in one file.
- **Typed, immutable handoffs.** Messages are frozen dataclasses, not free-form strings. Each step's output can be inspected, logged in `RunResult.steps`, and asserted on in tests.
- **The LLM is injected.** Agents receive an `LLMClient` in their constructor. Tests pass a `StubLLMClient` with canned responses, so the pipeline is deterministic and needs no API key. A real provider (v0.2) is just another implementation of the protocol.
- **One input per agent.** When an agent needs several inputs (QA needs the plan and the changes), they are wrapped in a dedicated message (`ReviewRequest`) so `Agent.run` keeps a single-argument signature.
