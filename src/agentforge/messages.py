"""Typed messages passed between agents.

These dataclasses are the contract between agents. Each agent consumes one
message type and produces another, so agents can be built and tested in
isolation. Messages are frozen so a handoff can't be mutated downstream.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    """A feature request submitted to the orchestrator."""

    description: str


@dataclass(frozen=True)
class DesignPlan:
    """Architect output: what to change and how to tell when it's done."""

    summary: str
    files_to_change: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()


@dataclass(frozen=True)
class FileChange:
    """The new full contents of one file."""

    path: str
    content: str


@dataclass(frozen=True)
class CodeChange:
    """Developer output: the set of file changes implementing a plan."""

    summary: str
    files: tuple[FileChange, ...] = ()


@dataclass(frozen=True)
class DevelopmentRequest:
    """Developer input: the plan, plus the rejected attempt and QA findings on a retry."""

    plan: DesignPlan
    previous: CodeChange | None = None
    findings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.findings, tuple) or not all(
            isinstance(f, str) for f in self.findings
        ):
            raise TypeError("findings must be a tuple of strings")
        if self.previous is None and self.findings:
            raise ValueError("findings require a previous attempt")
        if self.previous is not None and not self.findings:
            raise ValueError("a previous attempt requires findings")


@dataclass(frozen=True)
class ReviewRequest:
    """QA input: the plan to check against and the changes to review."""

    plan: DesignPlan
    changes: CodeChange


@dataclass(frozen=True)
class ReviewReport:
    """QA output: whether the changes meet the plan, and why not if they don't."""

    passed: bool
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class StepRecord:
    """One agent call in a run, kept for the step log."""

    agent: str
    output: DesignPlan | CodeChange | ReviewReport


@dataclass(frozen=True)
class RunResult:
    """Orchestrator output: the final outcome plus every step taken."""

    task: Task
    passed: bool
    steps: tuple[StepRecord, ...] = ()
    attempts: int = 0
    failure: str | None = None
