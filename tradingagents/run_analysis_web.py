"""
ACCE v2.0 - Web 版分析脚本（完整 8 智能体 LangGraph，可被 Web 后端调用）

满血默认：多智能体辩论、新闻/基本面/技术面链路、智能路由（含加密货币与 A 股等）。
可选环境变量 ACCE_DIRECT_LLM_ONLY=1 时退回旧版「仅直连 LLM」模式（应急）。
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 设置输出编码为 UTF-8，避免 Windows GBK 问题
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


def _build_real_market_context(ticker: str, start_date: str, end_date: str, market_type: str) -> str:
    """直连 LLM 模式用：拉取行情摘要。"""
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
        summary = chart.get("summary") or {}
        ohlcv = chart.get("ohlcv") or {}
        dates = ohlcv.get("date") or []
        closes = ohlcv.get("close") or []
        n = min(len(dates), len(closes), 20)
        tail = []
        for i in range(max(0, len(dates) - n), len(dates)):
            tail.append(f"{dates[i]}: {closes[i]}")
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
    """应急：仅 LLM、无多智能体图。"""
    market_ctx = _build_real_market_context(ticker, start_date, end_date, market_type)
    lang = "Chinese" if (report_language or "zh").lower() in ("zh", "cn", "chinese") else "English"
    length_hint = "约1000字" if lang == "Chinese" else "about 600-800 words"
    prompt = f"""You are a professional equity analyst.
Use ONLY the provided real market data context and do not fabricate missing figures.
Do NOT use words like 模拟/演示/mock/demo/dummy/example/disclaimer in output.
Do NOT output disclaimer section.

Output language: {lang}
Length: {length_hint}
Required sections:
1) 核心观点 / Core View
2) 基本面简述 / Fundamentals
3) 技术分析 / Technicals
4) 风险提示 / Risks
5) 投资建议 / Recommendation

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
    """完整 TradingAgents 多智能体图。"""
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
        "Chinese" if (report_language or "zh").lower() in ("zh", "cn", "chinese") else "English"
    )

    # 满血：更高轮次与递归上限（可用环境变量覆盖）
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
        trade_config["data_vendors"]["core_stock_apis"] = "wrds"
        trade_config["data_vendors"]["fundamental_data"] = "wrds"
        print("[数据源] 美股历史区间：优先 WRDS（学术库）")
    elif mt == "us" and start_dt > cutoff_dt:
        trade_config["data_vendors"]["core_stock_apis"] = "alpha_vantage"
        trade_config["data_vendors"]["fundamental_data"] = "alpha_vantage"
        print("[数据源] 美股近期：Alpha Vantage / yfinance")
    elif mt == "cn":
        trade_config["data_vendors"]["core_stock_apis"] = "efinance"
        trade_config["data_vendors"]["fundamental_data"] = "efinance"
        print("[数据源] A 股：efinance / akshare 路由")

    trade_config = get_smart_config(ticker, trade_config)

    print("[模式] 完整多智能体 LangGraph（8 智能体 + 辩论/风险讨论）")
    print(f"[分析] 基准日 {end_date}，区间 {start_date} ~ {end_date}")

    ta = TradingAgentsGraph(debug=True, config=trade_config)
    _, decision = ta.propagate(ticker, end_date)
    return str(decision)


def main() -> None:
    if len(sys.argv) < 6:
        print("=" * 80)
        print(" " * 10 + "ACCE v2.0 - Web 集成（完整多智能体 / 可选直连 LLM）")
        print("=" * 80)
        print()
        print("用法:")
        print(
            "  python run_analysis_web.py <llm_choice> <ticker> <start_date> <end_date> "
            "<analysis_type> [market_type] [report_language]"
        )
        print()
        print("环境变量 ACCE_DIRECT_LLM_ONLY=1 时仅走直连 LLM（无多智能体）。")
        print()
        return

    llm_choice = sys.argv[1]
    raw_ticker = sys.argv[2].strip()
    start_date = sys.argv[3]
    end_date = sys.argv[4] if sys.argv[4] != "None" else datetime.now().strftime("%Y-%m-%d")
    analysis_type = sys.argv[5]
    market_type = sys.argv[6] if len(sys.argv) >= 7 else "us"
    report_language = sys.argv[7] if len(sys.argv) >= 8 else "zh"

    ticker = raw_ticker.upper() if (market_type or "us").lower() == "us" else raw_ticker

    print("[Loading] 正在加载 API 密钥...")
    api_keys = load_llm_api_keys()
    if api_keys:
        print(f"[OK] 已加载 {len(api_keys)} 个 LLM 密钥")

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
        print("[错误] 无效的分析师选择或缺少 API 密钥")
        sys.exit(1)

    print(f"[已确认] 使用 {config['name']}")

    market_names = {
        "us": "美股",
        "cn": "A股",
        "hk": "港股",
        "tw": "台股",
        "crypto": "加密货币",
    }
    print(f"[已确认] 市场: {market_names.get((market_type or 'us').lower(), market_type)}")
    print(f"[已确认] 标的 {ticker}，{start_date} ~ {end_date}")

    os.environ["ANALYSIS_START_DATE"] = start_date
    os.environ["ANALYSIS_END_DATE"] = end_date

    try:
        if os.environ.get("ACCE_DIRECT_LLM_ONLY", "").strip().lower() in ("1", "true", "yes"):
            print("[模式] 直连 LLM（ACCE_DIRECT_LLM_ONLY）")
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
        print("分析完成！")
        print("=" * 80)
        print()
        print(decision)
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print(f"[错误] 分析失败: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
