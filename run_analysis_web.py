"""
ACCE v2.0 - Web analysis runner (invoked by web_backend).

- Homework mode (ACCE_HOMEWORK_MODE=1, default): single direct LLM call with real chart context (fast).
  Set ACCE_HOMEWORK_USE_FULL_GRAPH=1 to run the full 8-agent LangGraph instead.
- Professional mode (ACCE_HOMEWORK_MODE=0): full multi-agent graph unless ACCE_DIRECT_LLM_ONLY=1.
"""

from __future__ import annotations

import os
import sys

from datetime import datetime
from dotenv import load_dotenv

# UTF-8 stdout/stderr on Windows (avoid GBK mojibake)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

from tradingagents.utils.credentials import load_llm_api_keys
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.smart_router import get_smart_config
from tradingagents.llm_clients import create_llm_client
from tradingagents.agents.utils.agent_utils import is_homework_simple_mode


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _use_direct_llm_path() -> bool:
    """Homework default: one-shot LLM; optional env overrides."""
    if _env_truthy("ACCE_DIRECT_LLM_ONLY"):
        return True
    if is_homework_simple_mode() and not _env_truthy("ACCE_HOMEWORK_USE_FULL_GRAPH"):
        return True
    return False


def _build_real_market_context(ticker: str, start_date: str, end_date: str, market_type: str) -> str:
    """Direct-LLM mode: fetch a compact market context string."""
    try:
        from fast_chart_data import get_wrds_chart_data

        chart = (
            get_wrds_chart_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                market_type=market_type,
            )
            or {}
        )
        inner = chart.get("data") if isinstance(chart.get("data"), dict) else chart
        summary = inner.get("summary") or {}
        ohlcv = inner.get("ohlcv") or {}
        indicators = inner.get("indicators") or {}
        dates = ohlcv.get("date") or []
        closes = ohlcv.get("close") or []
        n = min(len(dates), len(closes), 20)
        tail = []
        for i in range(max(0, len(dates) - n), len(dates)):
            tail.append(f"{dates[i]}: {closes[i]}")
        boll = indicators.get("BOLL") if isinstance(indicators.get("BOLL"), dict) else {}
        boll_snap = []
        if boll and closes:
            li = len(closes) - 1
            for label, key in (("upper", "UPPER"), ("middle", "MIDDLE"), ("lower", "LOWER")):
                arr = boll.get(key)
                if isinstance(arr, list) and li < len(arr) and arr[li] is not None:
                    try:
                        boll_snap.append(f"{label}: {round(float(arr[li]), 4)}")
                    except (TypeError, ValueError):
                        pass
        context_lines = [
            f"Ticker: {ticker}",
            f"Market: {market_type}",
            f"Range: {start_date} to {end_date}",
            f"Current: {summary.get('current')}",
            f"Change: {summary.get('change')} ({summary.get('change_pct')}%)",
            f"DataSource: {chart.get('data_source')}",
            "Recent closes:",
            *tail,
        ]
        if boll_snap:
            context_lines.extend(["Bollinger Bands (last bar, from chart pipeline):", ", ".join(boll_snap)])
        return "\n".join(str(x) for x in context_lines if x is not None)
    except Exception as e:
        return f"Ticker: {ticker}\nMarket: {market_type}\nRange: {start_date} to {end_date}\nData fetch failed: {e}"


def _generate_direct_llm_report(
    config: dict,
    ticker: str,
    start_date: str,
    end_date: str,
    market_type: str,
    report_language: str,
) -> str:
    """Emergency path: LLM only, no multi-agent graph."""
    market_ctx = _build_real_market_context(ticker, start_date, end_date, market_type)
    lang = "Chinese" if (report_language or "en").lower() in ("zh", "cn", "chinese") else "English"
    if is_homework_simple_mode():
        length_hint = "约550–900字" if lang == "Chinese" else "about 380–620 words"
        extra = (
            "\nCoursework depth: include (2) **basic fundamentals/financials** from credible general knowledge "
            "only where the context lacks filings—do not invent specific numbers; say unknown if needed. "
            "(3) **Technical analysis must discuss Bollinger Bands** using the provided upper/middle/lower snapshot "
            "if present; otherwise state bands are not in context and comment only on price action shown."
            if lang != "Chinese"
            else "\n作业深度：(2) **基本面与财务**要结合常识与上下文，不得编造具体财报数字；缺数据请写未知。(3) **技术分析必须讨论布林带**："
            "若上下文中给出上轨/中轨/下轨快照，须结合收盘价说明超买/超卖或贴轨；若无则写明并仅根据已有价格序列简述。"
        )
    else:
        length_hint = "约1000字" if lang == "Chinese" else "about 600–800 words"
        extra = ""
    prompt = f"""You are a professional equity analyst.
Use ONLY the provided real market data context and do not fabricate missing figures.
Do NOT use mock/demo/dummy/example/disclaimer framing in output.

Output language: {lang}
Length: {length_hint}
Required sections:
1) Core View
2) Fundamentals
3) Technical Analysis
4) Risk Factors
5) Investment Recommendation
{extra}

Market data context:
{market_ctx}
"""
    provider = "google" if config["provider"] == "google" else "openai"
    llm = create_llm_client(
        provider=provider,
        model=config["model"],
        base_url=config.get("url"),
        api_key=config.get("api_key"),
        timeout=120,
        max_retries=2,
    ).get_llm()
    res = llm.invoke(prompt)
    text = str(getattr(res, "content", res))
    filtered_lines = []
    for ln in text.splitlines():
        low = ln.lower()
        if any(x in ln for x in ("模拟", "演示", "免责声明")) or any(
            x in low for x in ("mock", "demo", "dummy", "example", "disclaimer")
        ):
            continue
        filtered_lines.append(ln)
    return "\n".join(filtered_lines).strip()


def _run_full_agent_graph(
    config: dict,
    ticker: str,
    start_date: str,
    end_date: str,
    market_type: str,
    report_language: str,
    analysis_type: str,
) -> str:
    """Full TradingAgents multi-agent graph."""
    trade_config = DEFAULT_CONFIG.copy()

    if config["provider"] == "openai":
        trade_config["llm_provider"] = "openai"
        trade_config["backend_url"] = config["url"]
        trade_config["deep_think_llm"] = config["model"]
        trade_config["quick_think_llm"] = config["model"]
        os.environ["OPENAI_API_KEY"] = config["api_key"]
    elif config["provider"] == "google":
        trade_config["llm_provider"] = "google"
        trade_config["deep_think_llm"] = config["model"]
        trade_config["quick_think_llm"] = config["model"]
        os.environ["GOOGLE_API_KEY"] = config["api_key"]

    trade_config["output_language"] = (
        "Chinese" if (report_language or "en").lower() in ("zh", "cn", "chinese") else "English"
    )

    # Debate / recursion limits (override via env)
    trade_config["max_debate_rounds"] = int(os.environ.get("ACCE_MAX_DEBATE_ROUNDS", "3"))
    trade_config["max_risk_discuss_rounds"] = int(os.environ.get("ACCE_MAX_RISK_ROUNDS", "3"))
    trade_config["max_recur_limit"] = int(os.environ.get("ACCE_MAX_RECUR_LIMIT", "200"))

    if analysis_type == "2":
        trade_config["max_debate_rounds"] = 1
        trade_config["max_risk_discuss_rounds"] = 1
    elif analysis_type == "3":
        trade_config["max_debate_rounds"] = 1
        trade_config["max_risk_discuss_rounds"] = 1

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    cutoff_dt = datetime(2024, 12, 31)

    trade_config["data_vendors"] = {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    }

    mt = (market_type or "us").lower()
    if mt == "us" and start_dt <= cutoff_dt:
        # Coursework: only OHLC uses WRDS; other categories stay on default vendors
        trade_config["data_vendors"]["core_stock_apis"] = "wrds"
        print("[Data] US historical window: OHLC -> WRDS (CRSP); fundamentals/indicators/news -> default vendors (non-WRDS)")
    elif mt == "us" and start_dt > cutoff_dt:
        trade_config["data_vendors"]["core_stock_apis"] = "alpha_vantage"
        trade_config["data_vendors"]["fundamental_data"] = "alpha_vantage"
        print("[Data] Recent US window: Alpha Vantage / yfinance")
    elif mt == "cn":
        trade_config["data_vendors"]["core_stock_apis"] = "efinance"
        trade_config["data_vendors"]["fundamental_data"] = "efinance"
        print("[Data] CN A-shares: efinance / akshare routing")

    trade_config = get_smart_config(ticker, trade_config)

    print("[Mode] Full multi-agent LangGraph (8 agents + debate / risk discussion)")
    print(f"[Analysis] As-of {end_date}, window {start_date} .. {end_date}")

    # Subprocess captures full stdout; graph debug pretty_prints would pollute the report panel.
    _graph_debug = os.environ.get("ACCE_GRAPH_DEBUG", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    ta = TradingAgentsGraph(debug=_graph_debug, config=trade_config)
    print("[Graph] Starting propagate() — this step may take several minutes (multiple LLM calls).", flush=True)
    _, decision = ta.propagate(ticker, end_date, squeeze_decision=False)
    print("[Graph] propagate() finished.", flush=True)
    return str(decision)


def main() -> None:
    if len(sys.argv) < 6:
        print("=" * 80)
        print(" " * 10 + "ACCE v2.0 - Web runner (homework=direct LLM by default)")
        print("=" * 80)
        print()
        print("Usage:")
        print(
            "  python run_analysis_web.py <llm_choice> <ticker> <start_date> <end_date> "
            "<analysis_type> [market_type] [report_language]"
        )
        print()
        print("Env: ACCE_HOMEWORK_MODE=1 (default) → direct LLM; ACCE_HOMEWORK_USE_FULL_GRAPH=1 → 8-agent graph.")
        print("     ACCE_HOMEWORK_MODE=0 → multi-agent graph; ACCE_DIRECT_LLM_ONLY=1 → always direct LLM.")
        print()
        return

    llm_choice = sys.argv[1]
    raw_ticker = sys.argv[2].strip()
    start_date = sys.argv[3]
    end_date = sys.argv[4] if sys.argv[4] != "None" else datetime.now().strftime("%Y-%m-%d")
    analysis_type = sys.argv[5]
    market_type = sys.argv[6] if len(sys.argv) >= 7 else "us"
    report_language = sys.argv[7] if len(sys.argv) >= 8 else "en"

    ticker = raw_ticker.upper() if (market_type or "us").lower() == "us" else raw_ticker

    print("[Loading] Loading API keys...")
    api_keys = load_llm_api_keys()
    if api_keys:
        print(f"[OK] Loaded {len(api_keys)} LLM key(s)")

    analyst_configs = {
        "1": {
            "name": "DeepSeek",
            "provider": "openai",
            "url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "api_key": api_keys.get("deepseek", "") if api_keys else "",
        },
        "2": {
            "name": "Kimi",
            "provider": "openai",
            "url": "https://api.moonshot.cn/v1",
            "model": "moonshot-v1-8k",
            "api_key": api_keys.get("kimi", "") if api_keys else "",
        },
        "3": {
            "name": "Gemini",
            "provider": "google",
            "model": "gemini-2.5-flash",
            "api_key": api_keys.get("gemini", "") if api_keys else "",
        },
    }

    config = analyst_configs.get(llm_choice)
    if not config or not config.get("api_key"):
        print("[Error] Invalid analyst choice or missing API key")
        sys.exit(1)

    print(f"[OK] Using {config['name']}")

    market_names = {
        "us": "US equities",
        "cn": "A-shares",
        "hk": "HK equities",
        "tw": "Taiwan",
        "crypto": "Crypto",
    }
    print(f"[OK] Market: {market_names.get((market_type or 'us').lower(), market_type)}")
    print(f"[OK] Ticker {ticker}, {start_date} .. {end_date}")

    os.environ["ANALYSIS_START_DATE"] = start_date
    os.environ["ANALYSIS_END_DATE"] = end_date

    try:
        if _use_direct_llm_path():
            if _env_truthy("ACCE_DIRECT_LLM_ONLY"):
                print("[Mode] Direct LLM (ACCE_DIRECT_LLM_ONLY)", flush=True)
            elif is_homework_simple_mode():
                print(
                    "[Mode] Homework: direct LLM (set ACCE_HOMEWORK_USE_FULL_GRAPH=1 for full 8-agent graph)",
                    flush=True,
                )
            else:
                print("[Mode] Direct LLM", flush=True)
            decision = _generate_direct_llm_report(
                config=config,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                market_type=market_type,
                report_language=report_language,
            )
        else:
            decision = _run_full_agent_graph(
                config=config,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                market_type=market_type,
                report_language=report_language,
                analysis_type=analysis_type,
            )

        print()
        print("=" * 80)
        print("Analysis complete.")
        print("=" * 80)
        print()
        print(decision, flush=True)
        print(flush=True)
        sys.stdout.flush()

    except Exception as e:
        print()
        print("=" * 80)
        print(f"[Error] Analysis failed: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
