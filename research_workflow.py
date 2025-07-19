"""Shared helper to run the investment research multi-agent workflow."""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Optional, Tuple

from agents import Runner
from financial_agents.config import build_financial_agents
from utils import output_file


async def run_research_async(
    question: str,
    *,
    max_turns: int = 40,
) -> Tuple[Optional[str], str]:
    """Run the full multi-agent workflow for *question*.

    Parameters
    ----------
    question : str
        The user question to research.
    max_turns : int, optional
        Safety cap for agent reasoning turns (default 40).

    Returns
    -------
    tuple
        (report_path, final_output) where:
          • *report_path* is an absolute path to the Markdown report (or ``None``)
          • *final_output* is the raw final_output string
    """

    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError(
            "OPENAI_API_KEY not set — set it as an environment variable before running."
        )

    bundle = build_financial_agents()

    async def _execute() -> str:
        return await Runner.run(bundle.head_pm, question, max_turns=max_turns)

    # Connect MCP servers (Yahoo Finance) while the workflow runs
    async with AsyncExitStack() as stack:
        for agent in [
            getattr(bundle, "fundamental", None),
            getattr(bundle, "quant", None),
        ]:
            if agent is None:
                continue
            for server in getattr(agent, "mcp_servers", []):
                await server.connect()
                await stack.enter_async_context(server)

        result = await _execute()

    # ------------------------------------------------------------------
    # Parse result to locate generated report file (if any)
    # ------------------------------------------------------------------
    report_path: Optional[str] = None
    try:
        if hasattr(result, "final_output"):
            output = result.final_output
            if isinstance(output, str):
                data = json.loads(output)
                if isinstance(data, dict) and "file" in data:
                    report_path = str(output_file(data["file"]))
        final_output_str = (
            result.final_output if hasattr(result, "final_output") else str(result)
        )
    except Exception:
        # Fall back to raw string representation
        final_output_str = str(result)

    return report_path, final_output_str


def run_research_sync(question: str):
    """Blocking wrapper around ``run_research_async`` suitable for Streamlit or CLIs."""

    return asyncio.run(run_research_async(question))
