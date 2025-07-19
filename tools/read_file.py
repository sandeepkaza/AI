import json
import pandas as pd
from agents import function_tool
from utils import output_file
from pathlib import Path


@function_tool
def read_file(filename: str, n_rows: int = 10) -> str:
    """
    Read and preview the contents of a file from the outputs directory.

    Supports reading CSV, Markdown (.md), and plain text (.txt) files. For CSV files, returns a preview of the last `n_rows` as a Markdown table. For Markdown and text files, returns the full text content. For unsupported file types, returns an error message.

    Args:
        filename: The name of the file to read, relative to the outputs directory. Supported extensions: .csv, .md, .txt.
        n_rows: The number of rows to preview for CSV files (default: 10).

    Returns:
        str: A JSON string containing either:
            - For CSV: {"file": filename, "preview_markdown": "<markdown table>"}
            - For Markdown/Text: {"file": filename, "content": "<text content>"}
            - For errors: {"error": "<error message>", "file": filename}
    """
    path = output_file(filename, make_parents=False)
    if not path.exists():
        return json.dumps({"error": "file not found", "file": filename})

    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        try:
            df = pd.read_csv(path).tail(n_rows)
            table_md = df.to_markdown(index=False)
            return json.dumps({"file": filename, "preview_markdown": table_md})
        except Exception as e:
            return json.dumps({"error": str(e), "file": filename})
    elif suffix == ".md" or suffix == ".txt":
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return json.dumps({"file": filename, "content": content})
        except Exception as e:
            return json.dumps({"error": str(e), "file": filename})
    else:
        return json.dumps(
            {"error": f"Unsupported file type: {suffix}", "file": filename}
        )
