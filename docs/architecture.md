# Architecture

This document describes how the code is organised. See the [README](../README.md) for the project goal and milestones.

## Pipeline

```
Task ──► Orchestrator
            │
            ├─► Architect   Task               ─► DesignPlan
            ├─► Developer   DevelopmentRequest ─► CodeChange    (repeated on QA rejection)
            │               (plan + previous change + findings)
            └─► QA          ReviewRequest      ─► ReviewReport
                            (plan + changes)
            ▼
         RunResult (passed, attempts, failure + StepRecord log)
```

## Feedback loop (v0.3)

The Orchestrator runs the Architect exactly once, then loops Developer -> QA until QA approves or the attempts run out. The total is `1 + max_retries` attempts (`max_retries` defaults to 2 and must be >= 0).

- **`DevelopmentRequest`** is the Developer's input: the plan, plus (on a retry) the previous `CodeChange` and QA's findings. The first request has no previous change and no findings; a retry must have both, and the message rejects any other combination.
- **Only the latest feedback is carried forward.** Attempt N sees attempt N-1's change and findings, not earlier ones.
- **Readiness rule.** If the plan has no `files_to_change` or no `acceptance_criteria`, the Orchestrator stops after the Architect step without calling the Developer (`attempts == 0`, `failure` set).
- **`RunResult.attempts` and `RunResult.failure`.** `attempts` counts Developer/QA rounds; `failure` is `None` on success and otherwise explains why the run failed (unready plan, or QA rejected every attempt with the last findings).
- **Malformed output is not retried.** An `AgentOutputError` from any agent still propagates out of `Orchestrator.run`; retries only cover well-formed QA rejections.

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
