import json
from pathlib import Path
from agents import function_tool
from utils import output_file


@function_tool
def generate_pdf(markdown_filename: str) -> str:
    """Convert a markdown file in outputs/ to a styled PDF.

    Parameters
    ----------
    markdown_filename : str
        Name of the markdown file (relative to outputs/). If extension is
        omitted, .md is assumed.

    Returns
    -------
    str
        JSON string with {"pdf_file": ..., "file": ...} or {"error": ...}.
    """
    # Ensure extension
    if not markdown_filename.endswith(".md"):
        markdown_filename += ".md"

    md_path = output_file(markdown_filename, make_parents=False)
    if not md_path.exists():
        return json.dumps({"error": "file not found", "file": markdown_filename})

    try:
        from markdown_pdf import MarkdownPdf, Section  # type: ignore
    except ImportError:
        return json.dumps(
            {
                "error": "markdown_pdf_not_installed",
                "detail": "Install it with: pip install markdown-pdf",
            }
        )

    try:
        text = Path(md_path).read_text(encoding="utf-8")
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        pdf.add_section(Section(text, root=str(output_file(""))))
        pdf_filename = markdown_filename.replace(".md", ".pdf")
        pdf_path = output_file(pdf_filename)
        pdf.save(str(pdf_path))
        return json.dumps({"pdf_file": pdf_filename, "file": pdf_filename})
    except Exception as e:
        return json.dumps({"error": str(e)})
