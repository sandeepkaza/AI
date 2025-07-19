import json
from agents import Agent, ModelSettings, function_tool, Runner, RunContextWrapper
from tools.write_markdown import write_markdown
from tools.read_file import read_file
from tools.list_output_files import list_output_files
from tools.generate_pdf import generate_pdf
from utils import compose_agent_prompt
from settings import DEFAULT_MODEL
from pydantic import BaseModel


class ReportEditorInput(BaseModel):
    fundamental: str
    macro: str
    quant: str
    pm: str
    files: list[str]


def build_editor_agent():
    editor_prompt = compose_agent_prompt("editor_base.md")

    return Agent(
        name="Report Editor Agent",
        instructions=editor_prompt,
        tools=[write_markdown, read_file, list_output_files, generate_pdf],
        model=DEFAULT_MODEL,
        model_settings=ModelSettings(temperature=0),
    )


def build_report_edit_tool(editor):
    @function_tool(
        name_override="report_editor",
        description_override="Stitch analysis sections into a Markdown report and save it. This is the ONLY way to generate and save the final investment report. All reports must be finalized through this tool.",
    )
    async def report_edit_tool(ctx: RunContextWrapper, input: ReportEditorInput) -> str:
        result = await Runner.run(
            starting_agent=editor,
            input=json.dumps(input.model_dump()),
            context=ctx.context,
            max_turns=40,
        )
        return result.final_output

    return report_edit_tool
