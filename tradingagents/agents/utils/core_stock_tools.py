from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime
import os
from tradingagents.dataflows.interface import route_to_vendor


def _clamp_to_analysis_window(start_date: str, end_date: str) -> tuple[str, str]:
    """
    Clamp tool-requested date range to the user-selected analysis window.
    Window is provided by run_analysis_web via env vars.
    """
    win_start = os.environ.get("ANALYSIS_START_DATE", "").strip()
    win_end = os.environ.get("ANALYSIS_END_DATE", "").strip()
    if not win_start or not win_end:
        return start_date, end_date

    try:
        s = datetime.strptime(start_date, "%Y-%m-%d")
        e = datetime.strptime(end_date, "%Y-%m-%d")
        ws = datetime.strptime(win_start, "%Y-%m-%d")
        we = datetime.strptime(win_end, "%Y-%m-%d")
    except Exception:
        return start_date, end_date

    # Normalize inverted inputs
    if s > e:
        s, e = e, s
    if ws > we:
        ws, we = we, ws

    clamped_s = max(s, ws)
    clamped_e = min(e, we)
    if clamped_s > clamped_e:
        # no overlap: fall back to strict user window
        clamped_s, clamped_e = ws, we

    return clamped_s.strftime("%Y-%m-%d"), clamped_e.strftime("%Y-%m-%d")


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
    """
    start_date, end_date = _clamp_to_analysis_window(start_date, end_date)
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)
