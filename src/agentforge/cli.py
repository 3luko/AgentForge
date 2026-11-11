"""Command-line entry point: `agentforge "<feature request>"`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.agents.base import AgentOutputError
from agentforge.demo import demo_llm
from agentforge.llm import LLMClient
from agentforge.messages import CodeChange, DesignPlan, ReviewReport, RunResult, Task


def _describe(output: DesignPlan | CodeChange | ReviewReport) -> str:
    if isinstance(output, DesignPlan):
        return f"{output.summary}; files: {', '.join(output.files_to_change)}"
    if isinstance(output, CodeChange):
        return f"{output.summary}; files: {', '.join(f.path for f in output.files)}"
    if output.passed:
        return "passed"
    return f"failed - {'; '.join(output.issues)}"


def format_result(result: RunResult) -> str:
    lines = [
        f"Task: {result.task.description}",
        f"Result: {'PASSED' if result.passed else 'FAILED'}",
    ]
    lines.append(f"Attempts: {result.attempts}")
    if result.failure:
        lines.append(f"Failure: {result.failure}")
    for i, step in enumerate(result.steps, start=1):
        lines.append(f"{i}. {step.agent}: {_describe(step.output)}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None, llm: LLMClient | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentforge",
        description="Turn a feature request into reviewed code using a team of agents.",
    )
    parser.add_argument("request", help="the feature request to build")
    args = parser.parse_args(argv)

    if llm is None:
        print("Running against the stub LLM (canned demo responses).", file=sys.stderr)
        llm = demo_llm()
    orchestrator = Orchestrator(Architect(llm), Developer(llm), QA(llm))

    try:
        result = orchestrator.run(Task(description=args.request))
    except AgentOutputError as exc:
        print(f"agentforge: {exc}", file=sys.stderr)
        return 1

    print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
