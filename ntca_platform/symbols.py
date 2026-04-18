"""Resolve user input to canonical symbols for NTCA charts and DB keys."""

from __future__ import annotations

import re

from .config import CN_NAME_TO_SYMBOL, HK_NAME_TO_SYMBOL, TICKER_ALIASES


def _strip(s: str) -> str:
    return (s or "").strip()


def resolve_symbol(ticker: str, market: str) -> str:
    """
    Returns canonical ticker for API/DB (e.g. GOOGL, 300308, 0700.HK).
    market: 'us' | 'cn' | 'hk' | 'tw'
    """
    raw = _strip(ticker)
    if not raw:
        return ""

    # Chinese names
    if raw in CN_NAME_TO_SYMBOL:
        return CN_NAME_TO_SYMBOL[raw]
    if raw in HK_NAME_TO_SYMBOL:
        return HK_NAME_TO_SYMBOL[raw]

    u = raw.upper().replace(" ", "")

    if market == "us":
        if u in TICKER_ALIASES:
            return TICKER_ALIASES[u]
        return u.split(".")[0]

    if market == "cn":
        # digits only or 300308.SZ
        m = re.match(r"^(\d{6})", u.replace(".", ""))
        if m:
            return m.group(1)
        return u

    if market == "hk":
        if u.endswith(".HK"):
            parts = "".join(ch for ch in u.replace(".HK", "") if ch.isdigit())
            if parts:
                code = parts[-5:] if len(parts) > 4 else parts.zfill(4)
                return f"{code}.HK"
            return raw
        digits = "".join(ch for ch in u if ch.isdigit())
        if digits:
            code = digits[-5:] if len(digits) > 4 else digits.zfill(4)
            return f"{code}.HK"
        return raw

    if market == "tw":
        if u.endswith(".TW"):
            return u
        digits = "".join(filter(str.isdigit, u))
        if digits:
            return f"{digits}.TW"
        return u

    return u
