import json
from agents import function_tool
from utils import outputs_dir


@function_tool
def list_output_files(extension: str = None) -> str:
    """
    List all files in the outputs directory. Optionally filter by file extension (e.g., 'png', 'csv', 'md').
    Returns a JSON list of filenames.
    """
    out_dir = outputs_dir()
    if extension:
        files = [f.name for f in out_dir.glob(f"*.{extension}") if f.is_file()]
    else:
        files = [f.name for f in out_dir.iterdir() if f.is_file()]
    return json.dumps({"files": files})
