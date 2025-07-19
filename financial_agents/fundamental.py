from agents import Agent, WebSearchTool, ModelSettings
from utils import compose_agent_prompt, make_yahoo_mcp_server
from settings import DEFAULT_MODEL, DEFAULT_SEARCH_CONTEXT


def build_fundamental_agent():
    prompt = compose_agent_prompt("fundamental_base.md")
    yahoo_mcp_server = make_yahoo_mcp_server()

    return Agent(
        name="Fundamental Analysis Agent",
        instructions=prompt,
        mcp_servers=[yahoo_mcp_server],
        tools=[WebSearchTool(search_context_size=DEFAULT_SEARCH_CONTEXT)],
        model=DEFAULT_MODEL,
        model_settings=ModelSettings(parallel_tool_calls=True, temperature=0),
    )
