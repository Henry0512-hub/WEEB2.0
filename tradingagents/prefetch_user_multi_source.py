#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按指定标的，从 2020-01-01（可调）至今天，分别从各数据源拉取日线并保存到本地文件夹。

数据源与目录（默认根目录 data/user_prefetch/）：
  wrds/       美股 CRSP（需 WRDS 账号，失败则跳过该文件）
  yfinance/   Yahoo（美股/港股/台股；A 股部分代码 Yahoo 也可能有）
  akshare/    A 股（AkShare stock_zh_a_hist）
  efinance/   A 股（efinance stock.get_quote_history，再按日期截取）

用法示例：
  python prefetch_user_multi_source.py --config data/user_universe.json
  python prefetch_user_multi_source.py --symbols AAPL,NVDA,TSLA --market us
  python prefetch_user_multi_source.py --symbols 300308,002475 --market cn
  python prefetch_user_multi_source.py --start 2020-01-01 --end 2026-04-13 --also-sqlite

配置文件 JSON 示例（列表）：
  [
    {"symbol": "AAPL", "market": "us"},
    {"symbol": "300308", "market": "cn"},
    {"symbol": "0700.HK", "market": "hk"}
  ]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from typing import Any, Optional

import pandas as pd

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DEFAULT_START = "2020-01-01"
OUT_ROOT = os.path.join(ROOT, "data", "user_prefetch")


def _today() -> str:
    return date.today().strftime("%Y-%m-%d")


def _ensure_dirs(base: str) -> None:
    for sub in ("wrds", "yfinance", "akshare", "efinance", "meta"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)


def _save_df(df: Optional[pd.DataFrame], path: str) -> bool:
    if df is None or len(df) == 0:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = df.copy()
    if isinstance(out.index, pd.DatetimeIndex):
        out.index.name = "date"
    out.to_csv(path, encoding="utf-8-sig")
    return True


def _fetch_wrds_us(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    try:
        from fast_chart_data import get_wrds_data

        return get_wrds_data(symbol, start, end)
    except Exception as e:
        print(f"  [WRDS] {symbol} error: {e}")
        return None


def _fetch_yfinance(symbol: str, market: str, start: str, end: str) -> Optional[pd.DataFrame]:
    try:
        from ntca_platform.fetchers import (
            _yf_ticker_history,
            fetch_hk_yfinance,
            fetch_tw_yfinance,
            normalize_hk_symbol_yf,
            normalize_tw_symbol_yf,
        )
    except Exception as e:
        print(f"  [yfinance] import error: {e}")
        return None

    m = (market or "us").lower()
    if m == "us":
        return _yf_ticker_history(symbol.upper().strip(), start, end)
    if m == "hk":
        return fetch_hk_yfinance(symbol, start, end)
    if m == "tw":
        return fetch_tw_yfinance(symbol, start, end)
    if m == "cn":
        # 部分 A 股在 Yahoo 有代码：600519.SS / 000001.SZ
        code = "".join(filter(str.isdigit, symbol))[:6]
        if len(code) != 6:
            return None
        suf = ".SS" if code.startswith("6") else ".SZ"
        ysym = f"{code}{suf}"
        return _yf_ticker_history(ysym, start, end)
    return _yf_ticker_history(symbol, start, end)


def _fetch_akshare_cn(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    try:
        from ntca_platform.fetchers import fetch_cn_akshare

        return fetch_cn_akshare(symbol, start, end)
    except Exception as e:
        print(f"  [akshare] {symbol} error: {e}")
        return None


def _fetch_efinance_cn(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """A 股：efinance 全历史后按日期过滤。"""
    try:
        from tradingagents.utils.efinance_vendor import ensure_vendored_efinance

        ensure_vendored_efinance()
        import efinance as ef
    except Exception as e:
        print(f"  [efinance] import/skip: {e}")
        return None

    code = "".join(filter(str.isdigit, symbol))[:6]
    if len(code) != 6:
        return None
    try:
        data = ef.stock.get_quote_history(code)
    except Exception as e:
        print(f"  [efinance] {symbol} api error: {e}")
        return None
    if data is None or data.empty:
        return None
    date_col = "日期" if "日期" in data.columns else None
    if date_col is None:
        for c in data.columns:
            if "日" in str(c):
                date_col = c
                break
    if date_col is None:
        return None
    data = data.copy()
    data[date_col] = pd.to_datetime(data[date_col])
    sd, ed = pd.Timestamp(start), pd.Timestamp(end)
    data = data[(data[date_col] >= sd) & (data[date_col] <= ed)]
    if data.empty:
        return None
    col_map = {
        "开盘": "OPEN",
        "最高": "HIGH",
        "最低": "LOW",
        "收盘": "CLOSE",
        "成交量": "VOLUME",
    }
    for k in list(col_map.keys()):
        if k not in data.columns:
            return None
    out = pd.DataFrame(
        {
            "OPEN": pd.to_numeric(data["开盘"], errors="coerce"),
            "HIGH": pd.to_numeric(data["最高"], errors="coerce"),
            "LOW": pd.to_numeric(data["最低"], errors="coerce"),
            "CLOSE": pd.to_numeric(data["收盘"], errors="coerce"),
            "VOLUME": pd.to_numeric(data["成交量"], errors="coerce").fillna(0).astype(int),
        },
        index=pd.to_datetime(data[date_col]),
    )
    out.sort_index(inplace=True)
    out.index = pd.to_datetime([pd.Timestamp(x).date() for x in out.index])
    return out


def _safe_filename(sym: str) -> str:
    s = sym.replace("/", "_").replace("\\", "_")
    return s if s.endswith(".csv") else f"{s}.csv"


def run_one(
    symbol: str,
    market: str,
    start: str,
    end: str,
    out_root: str,
    also_sqlite: bool,
    manifest: dict[str, Any],
) -> None:
    m = (market or "us").lower()
    key = f"{m}:{symbol}"
    manifest[key] = {"symbol": symbol, "market": m, "sources": {}}

    # ----- yfinance（各市场都尝试，独立文件） -----
    ydf = _fetch_yfinance(symbol, m, start, end)
    ypath = os.path.join(out_root, "yfinance", _safe_filename(symbol.replace(".", "_")))
    if _save_df(ydf, ypath):
        print(f"  [OK] yfinance -> {ypath} ({len(ydf)} rows)")
        manifest[key]["sources"]["yfinance"] = {"path": ypath, "rows": len(ydf)}
    else:
        print(f"  [--] yfinance skip {symbol}")
        manifest[key]["sources"]["yfinance"] = None

    if m == "us":
        wdf = _fetch_wrds_us(symbol, start, end)
        wpath = os.path.join(out_root, "wrds", _safe_filename(symbol))
        if _save_df(wdf, wpath):
            print(f"  [OK] wrds -> {wpath} ({len(wdf)} rows)")
            manifest[key]["sources"]["wrds"] = {"path": wpath, "rows": len(wdf)}
        else:
            print(f"  [--] wrds skip {symbol} (no creds or no data)")
            manifest[key]["sources"]["wrds"] = None

    if m == "cn":
        adf = _fetch_akshare_cn(symbol, start, end)
        apath = os.path.join(out_root, "akshare", _safe_filename(symbol))
        if _save_df(adf, apath):
            print(f"  [OK] akshare -> {apath} ({len(adf)} rows)")
            manifest[key]["sources"]["akshare"] = {"path": apath, "rows": len(adf)}
        else:
            print(f"  [--] akshare skip {symbol}")
            manifest[key]["sources"]["akshare"] = None

        edf = _fetch_efinance_cn(symbol, start, end)
        epath = os.path.join(out_root, "efinance", _safe_filename(symbol))
        if _save_df(edf, epath):
            print(f"  [OK] efinance -> {epath} ({len(edf)} rows)")
            manifest[key]["sources"]["efinance"] = {"path": epath, "rows": len(edf)}
        else:
            print(f"  [--] efinance skip {symbol}")
            manifest[key]["sources"]["efinance"] = None

    if also_sqlite:
        try:
            from ntca_platform.local_bars_db import upsert_dataframe

            # 优先用 yfinance 结果写入统一库；A 股可优先 akshare
            primary = ydf
            src_tag = "yfinance"
            if m == "cn" and adf is not None and len(adf) > 0:
                primary = adf
                src_tag = "akshare"
            if primary is not None and len(primary) > 0:
                n = upsert_dataframe(symbol, m, primary, src_tag)
                print(f"  [SQLite] upsert {symbol} {n} rows ({src_tag})")
                manifest[key]["sqlite_rows"] = n
        except Exception as e:
            print(f"  [SQLite] error: {e}")


def load_universe(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.config:
        path = args.config if os.path.isabs(args.config) else os.path.join(ROOT, args.config)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise SystemExit("config JSON must be a list of {symbol, market}")
        return data
    if args.symbols:
        syms = [s.strip() for s in args.symbols.split(",") if s.strip()]
        m = (args.market or "us").lower()
        return [{"symbol": s, "market": m} for s in syms]
    default_path = os.path.join(ROOT, "data", "user_universe.json")
    if os.path.isfile(default_path):
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise SystemExit(
        "请指定 --config 或 --symbols，或创建 data/user_universe.json\n"
        "示例: [{\"symbol\":\"AAPL\",\"market\":\"us\"}]"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="多数据源日线落盘（WRDS / yfinance / AkShare / efinance）")
    ap.add_argument("--config", help="JSON 列表：symbol + market")
    ap.add_argument("--symbols", help="逗号分隔代码，需配合 --market")
    ap.add_argument("--market", default="us", help="us|cn|hk|tw（--symbols 时使用）")
    ap.add_argument("--start", default=DEFAULT_START, help="开始日期 YYYY-MM-DD")
    ap.add_argument("--end", default=None, help="结束日期，默认今天")
    ap.add_argument("--out", default=OUT_ROOT, help="输出根目录")
    ap.add_argument("--also-sqlite", action="store_true", help="同时写入 data/ntca/ntca_bars.sqlite3")
    args = ap.parse_args()

    end = args.end or _today()
    start = args.start
    out_root = os.path.abspath(args.out)
    _ensure_dirs(out_root)

    universe = load_universe(args)
    manifest: dict[str, Any] = {
        "start": start,
        "end": end,
        "out_root": out_root,
        "items": {},
    }

    print("=" * 72)
    print(f"多数据源预取 | {start} .. {end}")
    print(f"输出目录: {out_root}")
    print(f"标的数: {len(universe)}")
    print("=" * 72)

    for item in universe:
        sym = item.get("symbol") or item.get("ticker")
        mkt = item.get("market", "us")
        if not sym:
            continue
        print(f"\n>> {sym} [{mkt}]")
        run_one(sym.strip(), str(mkt).lower(), start, end, out_root, args.also_sqlite, manifest["items"])

    meta_path = os.path.join(out_root, "meta", "manifest.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("\n" + "=" * 72)
    print(f"完成。清单: {meta_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
