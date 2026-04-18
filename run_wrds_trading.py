
"""
WRDS数据分析模式 - 使用WRDS数据库进行专业的金融数据分析
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create config optimized for WRDS data source
config = DEFAULT_CONFIG.copy()

# Configure to use WRDS as primary data source
config["data_vendors"] = {
    "core_stock_apis": "wrds",              # Use WRDS CRSP for stock prices
    "technical_indicators": "yfinance",      # WRDS data + yfinance indicators
    "fundamental_data": "wrds",             # Use WRDS Compustat for fundamentals
    "news_data": "yfinance",                # WRDS does not have news
}

# Optional: Tool-level configuration for more control
config["tool_vendors"] = {
    "get_stock_data": "wrds",
    "get_fundamentals": "wrds",
    "get_balance_sheet": "wrds",
    "get_cashflow": "wrds",
    "get_income_statement": "wrds",
}

# 重要：设置全局配置，这样数据流路由才能使用正确的配置
set_config(config)

print("=" * 70)
print("WRDS数据分析模式")
print("=" * 70)
print()
print("数据源配置:")
print(f"  - 股票价格数据: WRDS CRSP (学术研究级数据)")
print(f"  - 基本面数据: WRDS Compustat (专业财务数据库)")
print(f"  - 技术指标: yfinance")
print(f"  - 新闻数据: yfinance")
print()

# Initialize TradingAgents with WRDS config
try:
    print("正在初始化TradingAgents...")
    ta = TradingAgentsGraph(debug=True, config=config)
    print("✓ TradingAgents初始化成功 (WRDS数据源)")
    print()

    # Example: Analyze a stock using WRDS data
    ticker = input("请输入股票代码 (例如: AAPL, MSFT, TSLA): ").strip().upper()
    date = input("请输入分析日期 (格式: YYYY-MM-DD, 留空使用今天): ").strip()

    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    print()
    print(f"正在分析 {ticker} ({date})...")
    print("数据来源: WRDS (Wharton Research Data Services)")
    print()

    # Run analysis
    print("正在获取数据并分析...")
    _, decision = ta.propagate(ticker, date)

    print()
    print("=" * 70)
    print("分析结果:")
    print("=" * 70)
    print(decision)

except KeyboardInterrupt:
    print("\n\n用户取消操作")
except Exception as e:
    print(f"\n✗ 错误: {type(e).__name__}: {str(e)}")
    print("\n故障排除:")
    print("1. 检查WRDS连接: python test_wrds.py")
    print("2. 确认股票代码正确 (美股代码)")
    print("3. 检查网络连接")
    print("4. 查看详细错误信息")

    import traceback
    if "--debug" in input("\n输入 --debug 查看详细错误信息: "):
        print("\n详细错误:")
        traceback.print_exc()

