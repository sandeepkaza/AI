from agents import Agent, WebSearchTool, ModelSettings
from tools.get_fred_series import get_fred_series
from utils import compose_agent_prompt
from settings import DEFAULT_MODEL, DEFAULT_SEARCH_CONTEXT


def build_macro_agent():
    prompt = compose_agent_prompt("macro_base.md")
    return Agent(
        name="Macro Analysis Agent",
        instructions=prompt,
        tools=[
            WebSearchTool(search_context_size=DEFAULT_SEARCH_CONTEXT),
            get_fred_series,
        ],
        model=DEFAULT_MODEL,
        model_settings=ModelSettings(parallel_tool_calls=True, temperature=0),
    )
