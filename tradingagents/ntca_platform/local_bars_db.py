"""SQLite store for daily OHLCV (NTCA offline / DB mode)."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd

from .config import DATA_START

_DB_PATH = None


def get_db_path() -> str:
    global _DB_PATH
    if _DB_PATH is None:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        d = os.path.join(root, "data", "ntca")
        os.makedirs(d, exist_ok=True)
        _DB_PATH = os.path.join(d, "ntca_bars.sqlite3")
    return _DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_bars (
            symbol TEXT NOT NULL,
            market TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            source TEXT,
            PRIMARY KEY (symbol, trade_date)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_daily_bars_sym_date ON daily_bars(symbol, trade_date)"
    )
    return conn


def upsert_dataframe(symbol: str, market: str, df: pd.DataFrame, source: str) -> int:
    """Expects df index DatetimeIndex and columns OPEN,HIGH,LOW,CLOSE,VOLUME."""
    if df is None or len(df) == 0:
        return 0
    conn = _connect()
    n = 0
    for idx, row in df.iterrows():
        d = pd.Timestamp(idx).strftime("%Y-%m-%d")
        conn.execute(
            """
            INSERT OR REPLACE INTO daily_bars
            (symbol, market, trade_date, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                market,
                d,
                float(row["OPEN"]),
                float(row["HIGH"]),
                float(row["LOW"]),
                float(row["CLOSE"]),
                int(row["VOLUME"]) if pd.notna(row["VOLUME"]) else 0,
                source,
            ),
        )
        n += 1
    conn.commit()
    conn.close()
    return n


def load_range(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """Load bars for symbol between dates (inclusive). Returns WRDS-style DataFrame or None."""
    conn = _connect()
    try:
        q = """
        SELECT trade_date, open, high, low, close, volume
        FROM daily_bars
        WHERE symbol = ? AND trade_date >= ? AND trade_date <= ?
        ORDER BY trade_date
        """
        df = pd.read_sql_query(q, conn, params=(symbol, start, end))
    finally:
        conn.close()
    if df is None or len(df) == 0:
        return None
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df.set_index("trade_date", inplace=True)
    df.rename(
        columns={
            "open": "OPEN",
            "high": "HIGH",
            "low": "LOW",
            "close": "CLOSE",
            "volume": "VOLUME",
        },
        inplace=True,
    )
    return df


def clamp_to_ntca_window(start: str, end: str) -> tuple[str, str]:
    """Restrict to DATA_START .. today."""
    lo = max(start, DATA_START)
    today = datetime.now().strftime("%Y-%m-%d")
    hi = min(end, today)
    if lo > hi:
        return DATA_START, today
    return lo, hi
