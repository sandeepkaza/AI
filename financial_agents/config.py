from dataclasses import dataclass
from financial_agents.fundamental import build_fundamental_agent
from financial_agents.macro import build_macro_agent
from financial_agents.quant import build_quant_agent
from financial_agents.editor import build_editor_agent, build_report_edit_tool
from financial_agents.pm import build_head_pm_agent


@dataclass
class FinancialAgentsBundle:
    head_pm: object
    fundamental: object
    macro: object
    quant: object


def build_financial_agents() -> FinancialAgentsBundle:
    fundamental = build_fundamental_agent()
    macro = build_macro_agent()
    quant = build_quant_agent()
    editor = build_editor_agent()
    report_edit_tool = build_report_edit_tool(editor)
    head_pm = build_head_pm_agent(fundamental, macro, quant, report_edit_tool)

    return FinancialAgentsBundle(
        head_pm=head_pm,
        fundamental=fundamental,
        macro=macro,
        quant=quant,
    )
