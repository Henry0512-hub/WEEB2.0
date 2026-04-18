"""One-off prefetch: WRDS (US) + AkShare (A) + yfinance Tickers 批量 (HK/TW/US fallback) -> SQLite."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ntca_platform.config import DATA_START, PREFETCH_UNIVERSE, today_iso, PLATFORM_NAME
from ntca_platform.fetchers import (
    batch_yfinance_history,
    fetch_cn_akshare,
    fetch_tw_yfinance,
    normalize_hk_symbol_yf,
)
from ntca_platform.local_bars_db import upsert_dataframe
from ntca_platform.symbols import resolve_symbol


def run_prefetch() -> None:
    from fast_chart_data import get_wrds_data

    start = DATA_START
    end = today_iso()
    print(f"[{PLATFORM_NAME}] Prefetch {start} .. {end}")

    universe = list(PREFETCH_UNIVERSE)
    us_items = [x for x in universe if x["market"] == "us"]
    hk_items = [x for x in universe if x["market"] == "hk"]
    tw_items = [x for x in universe if x["market"] == "tw"]
    cn_items = [x for x in universe if x["market"] == "cn"]

    # ----- US: WRDS 优先，失败则一次性批量 yfinance -----
    failed_us: list[str] = []
    for item in us_items:
        sym = item["symbol"]
        label = item.get("label", sym)
        df = get_wrds_data(sym, start, end)
        if df is not None and len(df) > 0:
            n = upsert_dataframe(sym, "us", df, "wrds")
            print(f"  [OK] {sym} ({label}) {n} rows source=wrds")
        else:
            failed_us.append(sym)
            print(f"  [WRDS miss] {sym}, will batch yfinance")

    if failed_us:
        batch = batch_yfinance_history(failed_us, start, end)
        for sym in failed_us:
            df = batch.get(sym)
            label = next((x.get("label", sym) for x in us_items if x["symbol"] == sym), sym)
            if df is not None and len(df) > 0:
                n = upsert_dataframe(sym, "us", df, "yfinance")
                print(f"  [OK] {sym} ({label}) {n} rows source=yfinance_batch")
            else:
                print(f"  [SKIP] {sym} ({label}) yfinance batch")

    # ----- HK: 单次 Tickers 批量 -----
    if hk_items:
        hk_yf_syms = []
        for item in hk_items:
            k = resolve_symbol(item["symbol"], "hk") or normalize_hk_symbol_yf(item["symbol"])
            if k:
                hk_yf_syms.append(k)
        if hk_yf_syms:
            batch_hk = batch_yfinance_history(hk_yf_syms, start, end)
            for item in hk_items:
                sym_key = resolve_symbol(item["symbol"], "hk") or item["symbol"]
                df = batch_hk.get(sym_key)
                if df is None and sym_key in batch_hk:
                    df = batch_hk[sym_key]
                if df is None:
                    for k, v in batch_hk.items():
                        if str(k).upper() == str(sym_key).upper():
                            df = v
                            break
                label = item.get("label", sym_key)
                if df is not None and len(df) > 0:
                    n = upsert_dataframe(sym_key, "hk", df, "yfinance_batch")
                    print(f"  [OK] {sym_key} ({label}) {n} rows source=yfinance_batch")
                else:
                    print(f"  [SKIP] {sym_key} ({label}) batch")

    # ----- TW: 批量 Tickers（可多档） -----
    if tw_items:
        tw_syms = []
        for item in tw_items:
            r = resolve_symbol(item["symbol"], "tw")
            if r:
                tw_syms.append(r)
        if tw_syms:
            batch_tw = batch_yfinance_history(tw_syms, start, end)
            for item in tw_items:
                sym_key = resolve_symbol(item["symbol"], "tw") or item["symbol"]
                df = batch_tw.get(sym_key)
                if df is None:
                    for k, v in batch_tw.items():
                        if str(k).upper() == str(sym_key).upper():
                            df = v
                            break
                label = item.get("label", sym_key)
                if df is not None and len(df) > 0:
                    n = upsert_dataframe(sym_key, "tw", df, "yfinance_batch")
                    print(f"  [OK] {sym_key} ({label}) {n} rows source=yfinance_batch")
                else:
                    df2 = fetch_tw_yfinance(item["symbol"], start, end)
                    if df2 is not None and len(df2) > 0:
                        n = upsert_dataframe(sym_key, "tw", df2, "yfinance")
                        print(f"  [OK] {sym_key} ({label}) {n} rows source=yfinance")
                    else:
                        print(f"  [SKIP] {sym_key} ({label})")

    # ----- A 股：AkShare 逐档 -----
    for item in cn_items:
        sym = item["symbol"]
        m = item["market"]
        label = item.get("label", sym)
        df = fetch_cn_akshare(sym, start, end)
        if df is not None and len(df) > 0:
            n = upsert_dataframe(sym, m, df, "akshare")
            print(f"  [OK] {sym} ({label}) {n} rows source=akshare")
        else:
            print(f"  [SKIP] {sym} ({label})")


if __name__ == "__main__":
    run_prefetch()
