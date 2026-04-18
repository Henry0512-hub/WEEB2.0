"""
ACCE v2.0 - 主分析程序
自动根据日期选择数据源，支持WRDS优先级
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入智能数据获取器
from intelligent_data_fetcher import IntelligentDataFetcher

# API密钥文件位置（自动加载）
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"
ALPHA_VANTAGE_API_FILE = r"C:\Users\lenovo\TradingAgents\av api.txt"
LLM_API_FILE = r"C:\Users\lenovo\Desktop\new\api assents.txt"


def load_llm_api_keys():
    """从文件加载LLM API密钥"""
    api_keys = {}

    if not os.path.exists(LLM_API_FILE):
        print(f"[WARNING] LLM API file not found: {LLM_API_FILE}")
        return api_keys

    try:
        with open(LLM_API_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 支持多种分隔符：: , = =
                if ':' in line:
                    key, value = line.split(':', 1)
                elif ',' in line:
                    key, value = line.split(',', 1)
                elif '=' in line:
                    key, value = line.split('=', 1)
                else:
                    continue

                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")

                api_keys[key] = value

        return api_keys

    except Exception as e:
        print(f"[ERROR] Failed to load LLM API keys: {e}")
        return api_keys


def get_analyst_config(choice, api_keys=None):
    """根据选择返回分析师配置（从文件加载API密钥）"""
    configs = {
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
        }
    }

    config = configs.get(choice)

    # 验证API密钥是否存在
    if config and not config.get("api_key"):
        print(f"[WARNING] API key for {config['name']} not found in {LLM_API_FILE}")
        print(f"[INFO] Please add '{choice.lower()}: YOUR_API_KEY' to the file")

    return config


def print_banner():
    """打印系统横幅"""
    print("=" * 80)
    print(" " * 20 + "ACCE v2.0 - Analysis System")
    print("=" * 80)
    print()


def main():
    """主函数"""

    print_banner()

    # 加载LLM API密钥
    print("[Loading] Loading LLM API keys...")
    api_keys = load_llm_api_keys()

    if api_keys:
        print(f"[OK] Loaded {len(api_keys)} LLM API key(s)")
        for provider in api_keys.keys():
            masked_key = api_keys[provider][:8] + "..." if len(api_keys[provider]) > 8 else "***"
            print(f"     - {provider.upper()}: {masked_key}")
    else:
        print("[WARNING] No LLM API keys loaded")

    print()

    # 步骤1：选择分析师
    print("Available Analysts:")
    print("  1. DeepSeek (Recommended) - Lowest cost: 1 RMB/million tokens")
    print("  2. Kimi (Chinese) - 128k context, best for Chinese")
    print("  3. Gemini (Free) - 1500 free requests per day")
    print()

    llm_choice = input("Please select your analyst (input 1-3): ").strip()

    config = get_analyst_config(llm_choice, api_keys)
    if not config:
        print("[Error] Invalid selection")
        input("Press Enter to exit...")
        sys.exit(1)

    if not config.get("api_key"):
        print(f"[ERROR] No API key found for {config['name']}")
        print(f"[INFO] Please add the API key to: {LLM_API_FILE}")
        print(f"[INFO] Format: {llm_choice.lower()}: YOUR_API_KEY")
        input("Press Enter to exit...")
        sys.exit(1)

    print(f"[Confirmed] You selected {config['name']} Analyst")
    print()

    # 步骤2：输入股票代码
    print("=" * 80)
    print()
    print("Common stock tickers:")
    print(" - US Stocks: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN")
    print(" - Chinese Stocks: BABA, JD, PDD, BIDU")
    print(" - Crypto: BTC-USD, ETH-USD")
    print()

    ticker = input("Please input stock ticker: ").strip().upper()
    print()

    # 步骤3：输入日期范围
    print("=" * 80)
    print()
    print("System will automatically select data source based on start date:")
    print()
    print(" - Start date 2024-12-31 or earlier: Use WRDS Academic Database ***")
    print(" - Start date after 2024-12-31: Use Real-time Data (Alpha Vantage)")
    print()
    print("Example date ranges:")
    print(" - Start: 2024-06-15, End: 2024-08-15 (Using WRDS, 2 months)")
    print(" - Start: 2025-01-15, End: 2025-03-20 (Real-time data, 2 months)")
    print()

    start_date = input("Please input start date (format: YYYY-MM-DD): ").strip()

    # 如果结束日期为空，使用今天
    end_date = input("Please input end date (format: YYYY-MM-DD, default today): ").strip()

    if end_date == "":
        # 获取今天的日期
        end_date = datetime.now().strftime("%Y-%m-%d")
        print(f"[Default] Using today as end date: {end_date}")

    print()
    print(f"[Confirmed] Analysis date range: {start_date} to {end_date}")

    # 计算天数差异
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days
        print(f"[Calculate] Analysis period: {days} days")
    except ValueError as e:
        print(f"[Error] Date format error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    print()
    print("=" * 80)
    print()
    print("Starting analysis system...")
    print()

    # 智能数据获取（自动降级）
    print("=" * 80)
    print("Intelligent Data Fetching System")
    print("=" * 80)
    print()
    print("Strategy:")
    print("  For US stocks before 2024-12-31:")
    print("    1. WRDS Academic Database (highest accuracy) ***")
    print("    2. Alpha Vantage API")
    print("    3. yfinance API")
    print("    4. Claw Crawler")
    print("    5. Mock Data")
    print()

    try:
        fetcher = IntelligentDataFetcher(ticker, start_date, end_date)
        stock_data, data_source = fetcher.fetch_stock_data()

        print()
        print(f"[Data Summary]")
        print(fetcher.get_data_summary(stock_data))

    except Exception as e:
        print()
        print(f"[Error] Data fetch failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    print()
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  Ticker: {ticker}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Data Source: {data_source}")
    print(f"  Analyst: {config['name']}")
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
