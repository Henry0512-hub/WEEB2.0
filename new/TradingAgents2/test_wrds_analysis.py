"""
测试WRDS历史数据分析 - 使用日期范围功能
测试2024年的数据（应该自动使用WRDS）
"""

import sys
import os
from datetime import datetime

# 添加TradingAgents路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 读取id.txt获取凭据
from pathlib import Path
id_file = Path(__file__).parent / "id.txt"
with open(id_file, 'r') as f:
    lines = f.readlines()
    wrds_username = lines[0].strip().split(': ')[1]
    wrds_password = lines[1].strip().split(': ')[1]

# 更新WRDS配置
import tradingagents.dataflows.wrds_source as wrds_source
wrds_source.WRDS_USERNAME = wrds_username
wrds_source.WRDS_PASSWORD = wrds_password

from intelligent_data_fetcher import IntelligentDataFetcher
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

print("="*70)
print("Testing WRDS Historical Data Analysis")
print("="*70)

# 测试案例：分析AAPL在2024年的表现
ticker = "AAPL"
start_date = "2024-06-15"
end_date = "2024-08-15"

print(f"\nTest Case:")
print(f"  Stock: {ticker}")
print(f"  Date Range: {start_date} to {end_date}")
print(f"  Period: {(datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days} days")
print()

# 判断是否应该使用WRDS
from run_enhanced_analysis import should_use_wrds
use_wrds = should_use_wrds(start_date)

print(f"[Data Source Selection]")
if use_wrds:
    print(f"  Start date ({start_date}) <= 2024-12-31")
    print(f"  -> Should use WRDS Academic Database")
else:
    print(f"  Start date ({start_date}) > 2024-12-31")
    print(f"  -> Should use Real-time Data")

print()
print("="*70)
print("Step 1: Testing WRDS Data Fetch")
print("="*70)
print()

# 创建WRDS连接
try:
    from tradingagents.dataflows.wrds_source import get_wrds_connection

    print("[Connecting] Connecting to WRDS...")
    db = get_wrds_connection()
    print("[Success] WRDS connection established!")

    # 测试查询历史数据
    print(f"\n[Query] Fetching {ticker} data from {start_date} to {end_date}...")

    # 获取permno
    symbol_sql = f"""
    SELECT permno, ticker, comnam
    FROM crsp.stocknames
    WHERE ticker = '{ticker.upper()}'
    ORDER BY namedt DESC
    LIMIT 1
    """

    stock_info = db.raw_sql(symbol_sql)
    print(f"[Found] Stock info: {stock_info['comnam'].iloc[0]} (permno: {stock_info['permno'].iloc[0]})")

    permno = stock_info['permno'].iloc[0]

    # 获取价格数据
    price_sql = f"""
    SELECT date, permno, prc AS close, bid AS bid, ask AS ask,
           shrout AS shares, vol AS volume
    FROM crsp.dsf
    WHERE permno = {permno}
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    ORDER BY date
    """

    price_data = db.raw_sql(price_sql, date_cols=['date'])
    print(f"[Success] Retrieved {len(price_data)} records")
    print(f"  Date range: {price_data['date'].min()} to {price_data['date'].max()}")
    print(f"  Price range: ${price_data['close'].abs().min():.2f} - ${price_data['close'].abs().max():.2f}")
    print(f"  Average volume: {price_data['volume'].mean():,.0f}")

    # 注意：不要关闭连接，让TradingAgents继续使用
    # db.close()  # 注释掉这行
    print("\n[Note] Keeping WRDS connection open for TradingAgents")

    print("\n" + "="*70)
    print("Step 2: Testing Intelligent Data Fetcher")
    print("="*70)
    print()

    # 测试智能数据获取器
    print(f"[Fetch] Using IntelligentDataFetcher for {ticker}...")
    fetcher = IntelligentDataFetcher(ticker, start_date, end_date)

    # 注意：由于yfinance对于历史日期可能返回空数据，
    # fetcher应该尝试yfinance，然后如果失败，使用模拟数据
    # 但对于WRDS数据，我们需要直接使用WRDS，而不是通过fetcher

    print()
    print("="*70)
    print("Step 3: Testing TradingAgents with WRDS")
    print("="*70)
    print()

    # 配置使用WRDS
    print("[Config] Setting up TradingAgents with WRDS...")

    # 使用DeepSeek配置
    analyst_config = {
        "name": "DeepSeek",
        "provider": "openai",
        "url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "api_key": "sk-d28ae30a58cb496c9b40e0029d0ef2c1"
    }

    os.environ["OPENAI_API_KEY"] = analyst_config["api_key"]

    trade_config = DEFAULT_CONFIG.copy()
    trade_config["llm_provider"] = "openai"
    trade_config["backend_url"] = analyst_config["url"]
    trade_config["deep_think_llm"] = analyst_config["model"]
    trade_config["quick_think_llm"] = analyst_config["model"]
    trade_config["output_language"] = "Chinese"

    # 配置使用WRDS数据源
    trade_config["data_vendors"] = {
        "core_stock_apis": "wrds",
        "fallback_apis": "yfinance"
    }

    print("[Init] Initializing TradingAgentsGraph...")
    ta = TradingAgentsGraph(debug=True, config=trade_config)

    print(f"\n[Analyze] Analyzing {ticker} from {start_date} to {end_date}...")
    print(f"[Base] Using {end_date} as analysis base date")
    print()

    # 运行分析
    _, decision = ta.propagate(ticker, end_date)

    print(f"\n{'='*70}")
    print(f"Analysis Complete!")
    print(f"{'='*70}")
    print(f"\n{decision}\n")

except Exception as e:
    print(f"\n[Error] Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Test Complete")
print("="*70)
