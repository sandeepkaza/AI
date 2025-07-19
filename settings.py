import os

# ---------------------------------------------------------------------------
# Model settings
# ---------------------------------------------------------------------------
# Default chat/completions model for all non-special cases
DEFAULT_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4.1-mini")
# Default model for PM
DEFAULT_PM_MODEL: str = os.getenv("DEFAULT_PM_MODEL", "gpt-4.1-mini")

# Dedicated model for Code Interpreter
CODE_INTERPRETER_MODEL: str = os.getenv("CODE_INTERPRETER_MODEL", DEFAULT_MODEL)

# ---------------------------------------------------------------------------
# Tool / search settings
# ---------------------------------------------------------------------------
# WebSearchTool context window ("small", "medium", "large")
DEFAULT_SEARCH_CONTEXT: str = os.getenv("DEFAULT_SEARCH_CONTEXT", "medium")

# Timeout (seconds) for Yahoo Finance MCP server sessions
YAHOO_MCP_TIMEOUT: int = int(os.getenv("YAHOO_MCP_TIMEOUT", "300"))

# ---------------------------------------------------------------------------
# Agent runtime defaults
# ---------------------------------------------------------------------------
# Safety cap for agent reasoning turns
DEFAULT_MAX_TURNS: int = int(os.getenv("DEFAULT_MAX_TURNS", "75"))
