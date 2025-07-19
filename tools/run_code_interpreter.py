import json
import os
import re
import requests
from agents import function_tool
from openai import OpenAI
from utils import output_file, repo_path
from settings import CODE_INTERPRETER_MODEL

PROMPT_PATH = repo_path("prompts/code_interpreter.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    CODE_INTERPRETER_INSTRUCTIONS = f.read()


def code_interpreter_error_handler(ctx, error):
    """
    Custom error handler for run_code_interpreter. Returns a clear message to the LLM about what went wrong and how to fix it.
    """
    return (
        "Error running code interpreter. "
        "You must provide BOTH a clear natural language analysis request and a non-empty list of input_files (relative to outputs/). "
        f"Details: {str(error)}"
    )


@function_tool(failure_error_function=code_interpreter_error_handler)
def run_code_interpreter(request: str, input_files: list[str]) -> str:
    """
    Executes a quantitative analysis request using OpenAI's Code Interpreter (cloud).

    Args:
        request (str): A clear, quantitative analysis request describing the specific computation, statistical analysis, or visualization to perform on the provided data.
            Examples:
                - "Calculate the Sharpe ratio for the portfolio returns in returns.csv."
                - "Plot a histogram of daily returns from the file 'AAPL_returns.csv'."
                - "Perform a linear regression of 'y' on 'x' in data.csv and report the R^2."
                - "Summarize the volatility of each ticker in the provided CSV."
        input_files (list[str]): A non-empty list of file paths (relative to outputs/) required for the analysis. Each file should contain the data needed for the requested quantitative analysis.
            Example: ["returns.csv", "tickers.csv"]

    Returns:
        str: JSON string with the analysis summary and a list of generated files (e.g., plots, CSVs) available for download.
    """
    # Input validation
    if not request or not isinstance(request, str):
        raise ValueError(
            "The 'request' argument must be a non-empty string describing the analysis to perform."
        )
    if (
        not input_files
        or not isinstance(input_files, list)
        or not all(isinstance(f, str) for f in input_files)
    ):
        raise ValueError(
            "'input_files' must be a non-empty list of file paths (strings) relative to outputs/."
        )

    client = OpenAI()
    file_ids = []
    for file_path in input_files:
        abs_path = output_file(file_path, make_parents=False)
        if not abs_path.exists():
            raise ValueError(
                f"File not found: {file_path}. "
                "Use the list_output_files tool to see which files exist, "
                "and the read_file tool to see the contents of CSV files."
            )
        with abs_path.open("rb") as f:
            uploaded = client.files.create(file=f, purpose="user_data")
            file_ids.append(uploaded.id)

    instructions = CODE_INTERPRETER_INSTRUCTIONS

    MAX_RETRIES = 3
    attempt = 0
    while True:
        try:
            resp = client.responses.create(
                model=CODE_INTERPRETER_MODEL,
                tools=[
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto", "file_ids": file_ids},
                    }
                ],
                instructions=instructions,
                input=request,
                temperature=0,
            )
            break  # Success
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                raise
            # Simple back-off; could be enhanced.
            continue

    output_text = resp.output_text
    # Extract container_id
    raw = resp.model_dump() if hasattr(resp, "model_dump") else resp.__dict__
    container_id = None
    if "output" in raw:
        for item in raw["output"]:
            if item.get("type") == "code_interpreter_call" and "container_id" in item:
                container_id = item["container_id"]

    # Download any new files
    downloaded_files = []
    if container_id:
        api_key = os.environ["OPENAI_API_KEY"]
        url = f"https://api.openai.com/v1/containers/{container_id}/files"
        headers = {"Authorization": f"Bearer {api_key}"}
        resp_files = requests.get(url, headers=headers)
        resp_files.raise_for_status()
        files = resp_files.json().get("data", [])
        for f in files:
            # Only download files not from user (i.e., generated)
            if f["source"] != "user":
                filename = f.get("path", "").split("/")[-1]
                cfile_id = f["id"]
                url_download = f"https://api.openai.com/v1/containers/{container_id}/files/{cfile_id}/content"
                resp_download = requests.get(url_download, headers=headers)
                resp_download.raise_for_status()
                out_path = output_file(filename)
                with open(out_path, "wb") as out:
                    out.write(resp_download.content)
                downloaded_files.append(str(out_path))

    # If no files were downloaded, raise error with <reason> tag if present
    if not downloaded_files:
        match = re.search(r"<reason>(.*?)</reason>", output_text, re.DOTALL)
        if match:
            reason = match.group(1).strip()
            raise ValueError(reason)
        raise ValueError(
            "No downloads were generated and no <reason> was provided. Please call the tool again, and ask for downloadable files."
        )

    return json.dumps(
        {
            "analysis": output_text,
            "files": downloaded_files,
        }
    )
