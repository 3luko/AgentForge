# AgentForge

AgentForge is a portfolio project for learning multi-agent software engineering. It is a small system where specialised AI agents work together to turn a feature request into reviewed, tested code.

## Goal

Learn, and show, how to design a multi-agent system that is:

- **Decomposed:** each agent has one clear job and a narrow interface.
- **Coordinated:** an orchestrator routes work between agents and tracks the state of a task.
- **Verifiable:** every agent hands off structured output that can be checked, logged and tested.
- **Understandable:** the code is small enough to read in one sitting, so the design choices are visible.

## Agents

| Agent | Responsibility | Input | Output |
|---|---|---|---|
| **Orchestrator** | Owns the task lifecycle. Calls the other agents in order, passes context between them, and decides when to retry or stop. | A feature request | Final result and a log of every step |
| **Architect** | Turns a request into a technical plan: files to touch, interfaces, and acceptance criteria. | Feature request | Design plan |
| **Developer** | Writes or changes code to carry out the plan. | Design plan | Code changes |
| **QA** | Checks the changes against the acceptance criteria and reports pass/fail with reasons. | Plan and code changes | Review report |

Planned flow:

```
request → Orchestrator → Architect → Developer → QA ─┬─ pass → done
                              ▲                      │
                              └──── fix requests ◄───┘ fail (bounded retries)
```

## Initial scope (v0.1)

- A single process running the agents in sequence. No concurrency or distributed execution.
- Agents talk through typed message objects, not free-form strings.
- An LLM client interface with a fake/stub implementation, so the whole pipeline can be tested without API calls.
- A command-line entry point that takes a feature request and prints the result and the step log.
- Unit tests for each agent and an end-to-end test of the pipeline using the stub client.

Out of scope for v0.1: a web UI, persistent storage, running code produced by agents in a sandbox, and parallel agents.

## Future milestones

1. **v0.1 – Skeleton pipeline:** project structure, message types, stub LLM, and a sequential orchestrator with placeholder agents.
2. **v0.2 – Real LLM integration:** connect a real model provider, with prompts kept per agent and config driven by environment variables.
3. **v0.3 – Feedback loop:** QA failures go back to the Developer, with a retry limit and the reasons for each failure carried forward.
4. **v0.4 – Tools and workspace:** agents read and write files in a scratch workspace, and QA runs the generated tests.
5. **v0.5 – Observability:** structured traces of every agent call (inputs, outputs, tokens, latency) and a run summary.
6. **v0.6 – Evaluation:** a small benchmark of feature requests with scoring, to compare prompts and models.
7. **Later:** parallel developer agents, a human-approval checkpoint, and a simple web dashboard for viewing runs.

## Status

v0.1 (skeleton pipeline) is complete. All four agents are implemented and run end to end against the stub LLM: `agentforge "add a login page"` prints the result and a step log using canned demo responses. v0.3 (feedback loop) is also implemented against the stub LLM: when QA rejects a change, the Orchestrator sends it back to the Developer with the findings, up to `max_retries` (default 2) times, and the result reports the number of attempts and any failure reason. The v0.2 real model provider is still to come.
