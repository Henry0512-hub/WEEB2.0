"""Fetch OHLCV via yfinance (Ticker / Tickers), AkShare, Alpha Vantage fallback."""

from __future__ import annotations

import concurrent.futures
from io import StringIO
from typing import Optional

import pandas as pd

# yfinance 单次请求超时（秒）；超时后美股/港股可试 Alpha Vantage
YFINANCE_TIMEOUT_SEC = 25.0
# 批量 Tickers 整包超时（秒）
YFINANCE_BATCH_TIMEOUT_SEC = 120.0


def _normalize_yf_df(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if df is None or len(df) == 0:
        return None
    df = df.rename(
        columns={
            "Open": "OPEN",
            "High": "HIGH",
            "Low": "LOW",
            "Close": "CLOSE",
            "Volume": "VOLUME",
        }
    )
    for c in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        if c not in df.columns:
            return None
    df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce").fillna(0).astype(int)
    df.index = pd.to_datetime([pd.Timestamp(x).date() for x in df.index])
    df.sort_index(inplace=True)
    return df[["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]


def _yf_ticker_history(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """
    单标的：yf.Ticker(symbol).history(start=, end=, auto_adjust=False)
    与官方推荐用法一致，避免不稳定连接。
    """
    import yfinance as yf

    end_ex = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    def _run():
        ticker = yf.Ticker(symbol)
        return ticker.history(start=start, end=end_ex, auto_adjust=False)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_run)
            df = fut.result(timeout=YFINANCE_TIMEOUT_SEC)
    except concurrent.futures.TimeoutError:
        return None
    except Exception:
        return None
    return _normalize_yf_df(df)


def _df_from_download_panel(raw: pd.DataFrame, ticker_key: str) -> Optional[pd.DataFrame]:
    """从 Tickers.download(group_by='ticker') 的面板中取单一标的 OHLCV。"""
    if raw is None or raw.empty or not isinstance(raw.columns, pd.MultiIndex):
        return None
    try:
        lvl_vals = list(raw.columns.get_level_values(1).unique())
        match = None
        for t in lvl_vals:
            if str(t).upper() == str(ticker_key).upper():
                match = t
                break
        if match is None:
            return None
        part = raw.xs(match, axis=1, level=1)
    except Exception:
        return None
    part = part.rename(
        columns={
            "Open": "OPEN",
            "High": "HIGH",
            "Low": "LOW",
            "Close": "CLOSE",
            "Volume": "VOLUME",
        }
    )
    for c in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        if c not in part.columns:
            return None
    part["VOLUME"] = pd.to_numeric(part["VOLUME"], errors="coerce").fillna(0).astype(int)
    part.index = pd.to_datetime([pd.Timestamp(x).date() for x in part.index])
    part.sort_index(inplace=True)
    return part[["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]


def batch_yfinance_history(
    symbols: list[str], start: str, end: str
) -> dict[str, pd.DataFrame]:
    """
    批量：优先 yf.Tickers(...).download(start,end) 合并拉取；失败再对每个
    ticker.history(...) 回退。降低请求次数（yahoo 限流时仍可能为空）。
    """
    import yfinance as yf

    symbols = [s.strip() for s in symbols if s and str(s).strip()]
    if not symbols:
        return {}

    end_ex = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    stock_str = " ".join(symbols)

    def _run() -> dict[str, pd.DataFrame]:
        out: dict[str, pd.DataFrame] = {}
        try:
            tickers = yf.Tickers(stock_str)
        except Exception:
            tickers = None

        if tickers is not None:
            try:
                raw = tickers.download(
                    start=start,
                    end=end_ex,
                    auto_adjust=False,
                    progress=False,
                    threads=True,
                    group_by="ticker",
                )
            except Exception:
                raw = None
            if raw is not None and not raw.empty:
                for sym in symbols:
                    nd = _df_from_download_panel(raw, sym)
                    if nd is not None and len(nd) > 0:
                        out[sym] = nd

        tmap = getattr(tickers, "tickers", {}) if tickers else {}
        for sym in symbols:
            if sym in out:
                continue
            try:
                tk = tmap.get(sym)
                if tk is None:
                    for k, v in tmap.items():
                        if str(k).upper() == str(sym).upper():
                            tk = v
                            break
                if tk is None:
                    tk = yf.Ticker(sym)
                df = tk.history(start=start, end=end_ex, auto_adjust=False)
                nd = _normalize_yf_df(df)
                if nd is not None and len(nd) > 0:
                    out[sym] = nd
            except Exception:
                nd = _yf_ticker_history(sym, start, end)
                if nd is not None and len(nd) > 0:
                    out[sym] = nd
        return out

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            return ex.submit(_run).result(timeout=YFINANCE_BATCH_TIMEOUT_SEC)
    except Exception:
        out: dict[str, pd.DataFrame] = {}
        for sym in symbols:
            nd = _yf_ticker_history(sym, start, end)
            if nd is not None and len(nd) > 0:
                out[sym] = nd
        return out


def normalize_hk_symbol_yf(symbol: str) -> str:
    """港股 Yahoo：xxxx.HK"""
    s = symbol.upper().strip()
    if not s.endswith(".HK"):
        digits = "".join(ch for ch in s if ch.isdigit())
        if not digits:
            return ""
        code = digits[-5:] if len(digits) > 4 else digits.zfill(4)
        s = f"{code}.HK"
    return s


def normalize_tw_symbol_yf(symbol: str) -> str:
    """台股：2330 或 2330.TW"""
    s = symbol.strip().upper().replace(" ", "")
    if s.endswith(".TW"):
        return s
    digits = "".join(filter(str.isdigit, s))
    if digits:
        return f"{digits}.TW"
    return s


def _alpha_csv_to_df(csv_str: str) -> Optional[pd.DataFrame]:
    if not csv_str or not csv_str.strip():
        return None
    s = csv_str.strip()
    if s.startswith("{") or s.startswith("["):
        return None
    try:
        df = pd.read_csv(StringIO(s))
    except Exception:
        return None
    if df is None or df.empty:
        return None
    df.columns = [str(c).strip().lower() for c in df.columns]
    ts_col = "timestamp" if "timestamp" in df.columns else df.columns[0]
    if ts_col not in df.columns:
        return None
    need = ("open", "high", "low", "close", "volume")
    if not all(c in df.columns for c in need):
        return None
    df[ts_col] = pd.to_datetime(df[ts_col])
    out = pd.DataFrame(
        {
            "OPEN": pd.to_numeric(df["open"], errors="coerce"),
            "HIGH": pd.to_numeric(df["high"], errors="coerce"),
            "LOW": pd.to_numeric(df["low"], errors="coerce"),
            "CLOSE": pd.to_numeric(df["close"], errors="coerce"),
            "VOLUME": pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int),
        },
        index=pd.to_datetime(df[ts_col]),
    )
    out.sort_index(inplace=True)
    out.index = pd.to_datetime([pd.Timestamp(x).date() for x in out.index])
    return out


def _fetch_alpha_vantage_daily(symbol_av: str, start: str, end: str) -> Optional[pd.DataFrame]:
    try:
        from tradingagents.dataflows.alpha_vantage_stock import get_stock
    except Exception:
        return None
    try:
        raw = get_stock(symbol_av, start, end)
    except Exception:
        return None
    return _alpha_csv_to_df(raw)


def _symbol_for_alpha_vantage_us(symbol: str) -> str:
    return symbol.upper().split(".")[0]


def _symbol_for_alpha_vantage_hk(hk_symbol: str) -> str:
    s = hk_symbol.upper().strip()
    if s.endswith(".HK"):
        return s.replace(".HK", ".HKG")
    return s


def fetch_us_yfinance(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    sym = _symbol_for_alpha_vantage_us(symbol)
    # 美股优先级：Alpha Vantage -> yfinance
    df = _fetch_alpha_vantage_daily(sym, start, end)
    if df is not None and len(df) > 0:
        return df
    return _yf_ticker_history(sym, start, end)


def fetch_tw_yfinance(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """台股：2330 / 2330.TW"""
    sym = normalize_tw_symbol_yf(symbol)
    if not sym:
        return None
    return _yf_ticker_history(sym, start, end)


def fetch_hk_yfinance(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    s = normalize_hk_symbol_yf(symbol)
    if not s:
        return None
    df = _yf_ticker_history(s, start, end)
    if df is not None and len(df) > 0:
        return df
    sym_av = _symbol_for_alpha_vantage_hk(s)
    df2 = _fetch_alpha_vantage_daily(sym_av, start, end)
    if df2 is not None and len(df2) > 0:
        return df2
    bare = "".join(filter(str.isdigit, s))[:5]
    if bare:
        return _fetch_alpha_vantage_daily(bare.zfill(4), start, end)
    return None


def fetch_cn_akshare(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    try:
        import akshare as ak
    except ImportError:
        return None
    code = "".join(filter(str.isdigit, symbol))[:6]
    if len(code) != 6:
        return None
    start_d = pd.Timestamp(start).strftime("%Y%m%d")
    end_d = pd.Timestamp(end).strftime("%Y%m%d")
    try:
        data = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_d,
            end_date=end_d,
            adjust="",
        )
    except Exception:
        return None
    if data is None or data.empty:
        return None
    if "日期" not in data.columns:
        return None
    data["日期"] = pd.to_datetime(data["日期"])
    out = pd.DataFrame(
        {
            "OPEN": pd.to_numeric(data["开盘"], errors="coerce"),
            "HIGH": pd.to_numeric(data["最高"], errors="coerce"),
            "LOW": pd.to_numeric(data["最低"], errors="coerce"),
            "CLOSE": pd.to_numeric(data["收盘"], errors="coerce"),
            "VOLUME": pd.to_numeric(data["成交量"], errors="coerce").fillna(0).astype(int),
        },
        index=pd.to_datetime(data["日期"]),
    )
    out.sort_index(inplace=True)
    return out


def fetch_cn_efinance(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    return fetch_cn_akshare(symbol, start, end)
