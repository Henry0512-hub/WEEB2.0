"""
WRDS + DeepSeek 分析模式
使用WRDS数据源 + DeepSeek API进行智能分析
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY", "").strip()
if not api_key:
    print("错误: 请通过 .env 或环境变量配置 OPENAI_API_KEY（DeepSeek 兼容）")
    sys.exit(1)

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config

# 创建配置 - 结合WRDS数据源和DeepSeek LLM
config = DEFAULT_CONFIG.copy()

# LLM配置 - 使用DeepSeek
config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"
config["output_language"] = "Chinese"

# 数据源配置 - 使用WRDS
config["data_vendors"] = {
    "core_stock_apis": "wrds",              # WRDS CRSP for stock prices
    "technical_indicators": "yfinance",      # yfinance for indicators
    "fundamental_data": "wrds",             # WRDS Compustat for fundamentals
    "news_data": "yfinance",                # yfinance for news
}

config["tool_vendors"] = {
    "get_stock_data": "wrds",
    "get_fundamentals": "wrds",
    "get_balance_sheet": "wrds",
    "get_cashflow": "wrds",
    "get_income_statement": "wrds",
}

# 性能优化配置
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 设置全局配置
set_config(config)

print("=" * 70)
print("WRDS + DeepSeek 智能分析模式")
print("=" * 70)
print()
print("配置信息:")
print(f"  LLM提供商: DeepSeek (deepseek-chat)")
print(f"  股票数据: WRDS CRSP (学术级数据库)")
print(f"  基本面数据: WRDS Compustat (专业财务数据库)")
print(f"  技术指标: yfinance")
print(f"  输出语言: 中文")
print()
print(f"✓ DeepSeek API密钥已加载: {api_key[:10]}...{api_key[-4:]}")
print()

try:
    print("正在初始化TradingAgents (DeepSeek + WRDS)...")
    ta = TradingAgentsGraph(debug=True, config=config)
    print("✓ 初始化成功！")
    print()

    # 获取用户输入
    ticker = input("请输入股票代码 (例如: AAPL, MSFT, TSLA): ").strip().upper()
    date = input("请输入分析日期 (格式: YYYY-MM-DD, 留空使用今天): ").strip()

    if not ticker:
        ticker = "AAPL"

    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    print()
    print("=" * 70)
    print(f"正在分析 {ticker} ({date})")
    print("数据来源: WRDS (Wharton Research Data Services)")
    print("AI引擎: DeepSeek")
    print("=" * 70)
    print()

    # 运行分析
    print("正在获取WRDS数据并进行AI分析...")
    print("(这可能需要30-60秒，请耐心等待...)")
    print()

    _, decision = ta.propagate(ticker, date)

    print()
    print("=" * 70)
    print("📊 分析结果:")
    print("=" * 70)
    print()
    print(decision)

except KeyboardInterrupt:
    print("\n\n用户取消操作")
except Exception as e:
    print(f"\n✗ 错误: {type(e).__name__}: {str(e)}")
    print()
    print("故障排除:")
    print("1. 确认DeepSeek API密钥已正确设置")
    print("2. 检查网络连接")
    print("3. 检查WRDS连接: python test_wrds.py")
    print("4. 确认股票代码正确 (美股代码)")

    import traceback
    show_debug = input("\n输入 y 查看详细错误信息: ")
    if show_debug.lower() == 'y':
        print("\n详细错误:")
        traceback.print_exc()
