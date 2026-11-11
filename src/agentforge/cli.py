"""Command-line entry point: `agentforge "<feature request>"`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from agentforge.agents import QA, Architect, Developer, Orchestrator
from agentforge.llm import StubLLMClient
from agentforge.messages import Task


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentforge",
        description="Turn a feature request into reviewed code using a team of agents.",
    )
    parser.add_argument("request", help="the feature request to build")
    args = parser.parse_args(argv)

    llm = StubLLMClient()
    orchestrator = Orchestrator(Architect(llm), Developer(llm), QA(llm))

    try:
        result = orchestrator.run(Task(description=args.request))
    except NotImplementedError as exc:
        print(f"agentforge: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
