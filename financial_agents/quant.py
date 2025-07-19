from agents import Agent, ModelSettings
from tools.run_code_interpreter import run_code_interpreter
from tools.get_fred_series import get_fred_series
from tools.read_file import read_file
from tools.list_output_files import list_output_files
from utils import compose_agent_prompt, make_yahoo_mcp_server
from settings import DEFAULT_MODEL


def build_quant_agent():
    prompt = compose_agent_prompt("quant_base.md")
    yahoo_mcp_server = make_yahoo_mcp_server()

    return Agent(
        name="Quantitative Analysis Agent",
        instructions=prompt,
        mcp_servers=[yahoo_mcp_server],
        tools=[run_code_interpreter, get_fred_series, read_file, list_output_files],
        model=DEFAULT_MODEL,
        model_settings=ModelSettings(parallel_tool_calls=True, temperature=0),
    )
