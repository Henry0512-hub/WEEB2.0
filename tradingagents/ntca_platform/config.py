"""NTCA Platform constants."""

from datetime import date

PLATFORM_NAME = "NTCA Platform"
PLATFORM_SHORT = "NTCA"

# Local DB only covers this range (assignment / product rule)
DATA_START = "2020-01-01"

# Universe: US names use CRSP tickers; A-share six-digit; HK as Yahoo symbols
PREFETCH_UNIVERSE = [
    # US (WRDS CRSP primary; yfinance fills DB if WRDS unavailable during prefetch)
    {"symbol": "AAPL", "market": "us", "label": "Apple"},
    {"symbol": "TSLA", "market": "us", "label": "Tesla"},
    {"symbol": "GOOGL", "market": "us", "label": "Alphabet"},
    {"symbol": "NVDA", "market": "us", "label": "NVIDIA"},
    {"symbol": "NFLX", "market": "us", "label": "Netflix"},
    # A-share (efinance / akshare family — not in CRSP US)
    {"symbol": "300308", "market": "cn", "label": "Zhongji Innolight"},
    {"symbol": "002475", "market": "cn", "label": "Luxshare"},
    {"symbol": "688256", "market": "cn", "label": "Cambricon"},
    # HK (yfinance *.HK) — 智谱 / MiniMax 非上市公司，无标准代码，不预取
    {"symbol": "0700.HK", "market": "hk", "label": "Tencent"},
    {"symbol": "9988.HK", "market": "hk", "label": "Alibaba"},
    # TW (yfinance *.TW)，例：台积电
    {"symbol": "2330", "market": "tw", "label": "TSMC"},
]

# Aliases user may type (uppercased in resolver)
TICKER_ALIASES = {
    "GOOGLE": "GOOGL",
    "GOOG": "GOOGL",
    "NETFLIX": "NFLX",
    "NETFLEX": "NFLX",
    "NVIDIA": "NVDA",
}

CN_NAME_TO_SYMBOL = {
    "中际旭创": "300308",
    "立讯精密": "002475",
    "寒武纪": "688256",
}

HK_NAME_TO_SYMBOL = {
    "腾讯": "0700.HK",
    "港股腾讯": "0700.HK",
    "阿里巴巴": "9988.HK",
    "阿里": "9988.HK",
}


def today_iso() -> str:
    return date.today().strftime("%Y-%m-%d")
