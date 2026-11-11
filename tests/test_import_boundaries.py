"""Only the Orchestrator may import other agents (see docs/architecture.md)."""

import ast
from pathlib import Path

import pytest

AGENTS_DIR = Path(__file__).parents[1] / "src" / "agentforge" / "agents"
ALLOWED = {"agentforge.agents.base", "agentforge.messages", "agentforge.llm"}


@pytest.mark.parametrize("module", ["architect", "developer", "qa"])
def test_worker_agents_import_only_base_messages_llm(module: str) -> None:
    tree = ast.parse((AGENTS_DIR / f"{module}.py").read_text(encoding="utf-8"))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("agentforge")
    }
    imported |= {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name.startswith("agentforge")
    }
    assert imported <= ALLOWED, f"{module}.py imports {imported - ALLOWED}"
