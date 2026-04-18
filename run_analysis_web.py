"""
ACCE v2.0 - Web版分析脚本
支持命令行参数，可以被Web后端调用
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime
from dotenv import load_dotenv

# 设置输出编码为UTF-8，避免Windows GBK编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 加载环境变量
load_dotenv()

from tradingagents.utils.credentials import get_is_dir, load_llm_api_keys
from tradingagents.llm_clients import create_llm_client

API_DIR = str(get_is_dir())
ALPHA_VANTAGE_API_FILE = os.path.join(API_DIR, "av api.txt")

def _is_transient_llm_network_error(err: Exception) -> bool:
    s = str(err).lower()
    marks = [
        "apiconnectionerror",
        "connection error",
        "connecterror",
        "unexpected_eof_while_reading",
        "ssl",
        "eof occurred in violation of protocol",
        "timed out",
        "timeout",
    ]
    return any(m in s for m in marks)


def _build_real_market_context(ticker: str, start_date: str, end_date: str, market_type: str) -> str:
    """Fetch real market data context for direct LLM reporting fallback."""
    try:
        from fast_chart_data import get_wrds_chart_data

        chart = get_wrds_chart_data(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            market_type=market_type,
        ) or {}
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


def _generate_direct_llm_report(config: dict, ticker: str, start_date: str, end_date: str, market_type: str, report_language: str) -> str:
    """Generate report by directly calling selected LLM with real data context."""
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
        timeout=60,
        max_retries=1,
    ).get_llm()
    res = llm.invoke(prompt)
    text = str(getattr(res, "content", res))
    banned = ("模拟", "演示", "mock", "demo", "dummy", "example", "免责声明", "disclaimer")
    filtered_lines = []
    for ln in text.splitlines():
        low = ln.lower()
        if any(x in ln for x in ("模拟", "演示", "免责声明")) or any(x in low for x in ("mock", "demo", "dummy", "example", "disclaimer")):
            continue
        filtered_lines.append(ln)
    return "\n".join(filtered_lines).strip()


def main():
    """主函数 - 支持命令行参数"""

    # 检查命令行参数
    if len(sys.argv) >= 6:
        # 从命令行参数读取
        llm_choice = sys.argv[1]
        ticker = sys.argv[2].upper()
        start_date = sys.argv[3]
        end_date = sys.argv[4] if sys.argv[4] != 'None' else datetime.now().strftime("%Y-%m-%d")
        analysis_type = sys.argv[5]
        market_type = sys.argv[6] if len(sys.argv) >= 7 else 'us'
        report_language = sys.argv[7] if len(sys.argv) >= 8 else 'zh'

        
    else:
        # 如果没有参数，使用交互模式
        print("=" * 80)
        print(" " * 15 + "ACCE v2.0 - 集成版完整分析系统")
        print("=" * 80)
        print()
        print("使用方法:")
        print("  python run_analysis_web.py <llm_choice> <ticker> <start_date> <end_date> <analysis_type> [market_type] [report_language]")
        print()
        print("示例:")
        print("  python run_analysis_web.py 1 AAPL 2024-06-15 2024-08-15 1 us zh")
        print("  python run_analysis_web.py 1 AAPL 2024-06-15 2024-08-15 1 us en")
        print("  python run_analysis_web.py 1 000001 2024-06-15 2024-08-15 1 cn zh")
        print()
        return

    # 加载LLM API密钥
    print("[Loading] 正在加载API密钥...")
    api_keys = load_llm_api_keys()

    if api_keys:
        print(f"[OK] 已加载 {len(api_keys)} 个LLM API密钥（来源: is/api assents.txt 及环境变量覆盖）")
    else:
        print("[WARNING] 未加载到LLM API密钥：请配置 is/api assents.txt 或 DEEPSEEK / KIMI / GEMINI 环境变量")

    # 映射到配置
    analyst_configs = {
        "1": {"name": "DeepSeek", "provider": "openai", "url": "https://api.deepseek.com/v1",
              "model": "deepseek-chat", "api_key": api_keys.get("deepseek", "")},
        "2": {"name": "Kimi", "provider": "openai", "url": "https://api.moonshot.cn/v1",
              "model": "moonshot-v1-8k", "api_key": api_keys.get("kimi", "")},
        "3": {"name": "Gemini", "provider": "google",
              "model": "gemini-2.5-flash", "api_key": api_keys.get("gemini", "")},
    }

    config = analyst_configs.get(llm_choice)
    if not config:
        print("[错误] 无效选择")
        sys.exit(1)

    if not config.get("api_key"):
        print(f"[错误] {config['name']} 的API密钥未找到")
        sys.exit(1)

    print(f"[已确认] 使用 {config['name']} 分析师")

    # 显示市场类型
    market_names = {
        'us': '美股',
        'cn': 'A股',
        'hk': '港股',
        'tw': '台股',
        'crypto': '加密货币'
    }
    print(f"[已确认] 市场: {market_names.get(market_type, '美股')}")
    print(f"[已确认] 分析 {ticker}（{start_date} 到 {end_date}）")
    # 给工具层提供硬约束窗口，避免模型自行扩大查询区间
    os.environ["ANALYSIS_START_DATE"] = start_date
    os.environ["ANALYSIS_END_DATE"] = end_date

    try:
        # 直接调用 LLM（禁用新闻链路，不走多智能体流程）
        print(f"[模式] 直连LLM报告模式（已禁用新闻功能）")
        print(f"[分析] 正在分析 {ticker}（分析周期: {start_date} 到 {end_date}）...")
        decision = _generate_direct_llm_report(
            config=config,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            market_type=market_type,
            report_language=report_language,
        )

        print()
        print("=" * 80)
        print("分析完成！")
        print("=" * 80)
        print()
        print(f"{decision}")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print(f"[错误] 分析失败: {e}")
        print("=" * 80)
        print("[提示] 当前是 LLM 网络连接异常，已保留行情与指标输出。")
        print("[提示] 请稍后重试，或切换分析师模型（如 Kimi/Gemini）。")
        print()


if __name__ == "__main__":
    main()
