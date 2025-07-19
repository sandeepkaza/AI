import os
import json
from agents import function_tool
from utils import output_file

# fredapi is optional; fall back gracefully if it isn't installed.
try:
    from fredapi import Fred  # type: ignore
except ImportError:  # pragma: no cover – optional dependency
    Fred = None  # type: ignore


@function_tool
def get_fred_series(
    series_id: str, start_date: str, end_date: str, download_csv: bool = False
) -> str:
    """Fetches a FRED economic time-series and returns simple summary statistics.

    Parameters
    ----------
    series_id : str
        FRED series identifier, e.g. "GDP" or "UNRATE".
    start_date : str
        ISO date string (YYYY-MM-DD).
    end_date : str
        ISO date string (YYYY-MM-DD).

    Returns
    -------
    str
        JSON string with basic statistics (mean, latest value, etc.). Falls back to a
        placeholder if fredapi is not available or an error occurs.
    """
    # Treat empty strings as unspecified
    start_date = start_date or None  # type: ignore
    end_date = end_date or None  # type: ignore

    if Fred is None:
        return json.dumps(
            {
                "error": "fredapi not installed. returning stub result",
                "series_id": series_id,
            }
        )

    try:
        fred_api_key = os.getenv("FRED_API_KEY")
        fred = Fred(api_key=fred_api_key)
        data = fred.get_series(
            series_id, observation_start=start_date, observation_end=end_date
        )
        if data is None or data.empty:
            return json.dumps(
                {"error": "Series not found or empty", "series_id": series_id}
            )

        summary = {
            "series_id": series_id,
            "observations": len(data),
            "start": str(data.index.min().date()),
            "end": str(data.index.max().date()),
            "latest": float(data.iloc[-1]),
            "mean": float(data.mean()),
        }

        # ------------------------------------------------------------------
        # Optional CSV download
        # ------------------------------------------------------------------
        if download_csv:
            # Reset index to turn the DatetimeIndex into a column for CSV output
            df = data.reset_index()
            df.columns = ["Date", series_id]  # Capital D to match Yahoo Finance

            # Build date_range string for filename (YYYYMMDD-YYYYMMDD).
            start_str = start_date if start_date else str(df["Date"].min().date())
            end_str = end_date if end_date else str(df["Date"].max().date())
            date_range = f"{start_str}_{end_str}".replace("-", "")
            file_name = f"{series_id}_{date_range}.csv"

            # Save under outputs/
            csv_path = output_file(file_name)
            df.to_csv(csv_path, index=False)

            # Add file metadata to summary
            summary["file"] = file_name
            summary["schema"] = ["Date", series_id]

        return json.dumps(summary)
    except Exception as e:
        return json.dumps({"error": str(e), "series_id": series_id})
