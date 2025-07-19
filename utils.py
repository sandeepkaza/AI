from __future__ import annotations

"""Shared utilities for the multi-agent investment workflow."""

from pathlib import Path
import os

# ---------------------------------------------------------------------------
# Global disclaimer for all agents
# ---------------------------------------------------------------------------

DISCLAIMER = (
    "DISCLAIMER: I am an AI language model, not a registered investment adviser. "
    "Information provided is educational and general in nature. Consult a qualified "
    "financial professional before making any investment decisions.\n\n"
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR: Path = Path(__file__).resolve().parent  # repository root


def repo_path(rel: str | Path) -> Path:
    """Return an absolute Path inside the repository given a relative string."""
    return (ROOT_DIR / rel).resolve()


def outputs_dir() -> Path:
    """Return the global `outputs/` folder, creating it if needed."""
    out = repo_path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Prompt loader
# ---------------------------------------------------------------------------

PROMPTS_DIR: Path = repo_path("prompts")


def load_prompt(name: str, **subs) -> str:
    """Load a Markdown prompt template and substitute <PLACEHOLDERS>."""
    content = (PROMPTS_DIR / name).read_text()
    for key, val in subs.items():
        content = content.replace(f"<{key}>", str(val))
    return content


# ---------------------------------------------------------------------------
# Output path helper
# ---------------------------------------------------------------------------


def output_file(name: str | Path, *, make_parents: bool = True) -> Path:
    """Return an absolute Path under the shared outputs/ directory.

    If *name* already starts with the string "outputs/", that prefix is removed
    to avoid accidentally nesting a second outputs folder (e.g.
    `outputs/outputs/foo.png`).  Absolute paths are returned unchanged.
    """

    path = Path(name)

    if path.is_absolute():
        return path

    # Strip leading "outputs/" if present
    if path.parts and path.parts[0] == "outputs":
        path = Path(*path.parts[1:])

    final = outputs_dir() / path

    if make_parents:
        final.parent.mkdir(parents=True, exist_ok=True)

    return final


# ---------------------------------------------------------------------------
# Agent helper utilities (prompt composition, shared MCP server, env checks)
# ---------------------------------------------------------------------------


def compose_agent_prompt(prompt_file: str, **subs) -> str:
    """Return full agent prompt with DISCLAIMER and retry instructions appended."""
    base = load_prompt(prompt_file, **subs)
    retry = load_prompt("tool_retry_prompt.md")
    return base + DISCLAIMER + retry


def make_yahoo_mcp_server():
    """Return a pre-configured Yahoo Finance MCPServerStdio instance."""
    from agents.mcp import (
        MCPServerStdio,
    )  # local import to avoid heavy dependency at import time
    from settings import YAHOO_MCP_TIMEOUT

    server_path = str(repo_path("tools/yahoo_finance_mcp.py"))
    return MCPServerStdio(
        params={"command": "python", "args": [server_path]},
        client_session_timeout_seconds=YAHOO_MCP_TIMEOUT,
        cache_tools_list=True,
    )


def ensure_env_vars(vars_: list[str]):
    """Raise an error if any of *vars_* env variables are missing."""
    missing = [v for v in vars_ if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(
            "Missing environment variable(s): "
            + ", ".join(missing)
            + ". Please set them before running."
        )


__all__ = [
    "ROOT_DIR",
    "repo_path",
    "outputs_dir",
    "load_prompt",
    "output_file",
    "compose_agent_prompt",
    "make_yahoo_mcp_server",
    "ensure_env_vars",
]
