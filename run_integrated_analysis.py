"""
ACCE v2.0 - 集成版完整分析系统
结合TradingAgents完整框架 + new目录的改进
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API密钥文件位置
LLM_API_FILE = r"C:\Users\lenovo\Desktop\new\api assents.txt"
ALPHA_VANTAGE_API_FILE = r"C:\Users\lenovo\TradingAgents\av api.txt"
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"


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


def print_banner():
    """打印系统横幅"""
    print("=" * 80)
    print(" " * 15 + "ACCE v2.0 - 集成版完整分析系统")
    print("=" * 80)
    print()
    print("功能特点:")
    print("  ✓ 完整TradingAgents框架（8个AI智能体）")
    print("  ✓ API密钥自动加载")
    print("  ✓ WRDS优先级设置")
    print("  ✓ 交互式用户界面")
    print("  ✓ 技术+基本面+情绪分析")
    print()


def main():
    """主函数 - 交互式完整分析"""

    print_banner()

    # 加载LLM API密钥
    print("[Loading] 正在加载API密钥...")
    api_keys = load_llm_api_keys()

    if api_keys:
        print(f"[OK] 已加载 {len(api_keys)} 个LLM API密钥:")
        for provider in api_keys.keys():
            masked_key = api_keys[provider][:8] + "..." if len(api_keys[provider]) > 8 else "***"
            print(f"     - {provider.upper()}: {masked_key}")
    else:
        print("[WARNING] 未加载到LLM API密钥")
    print()

    # 步骤1：选择分析师
    print("=" * 80)
    print("可选分析师（已从文件自动加载API密钥）")
    print("=" * 80)
    print("  1. DeepSeek（推荐）- 最低成本: ¥1/百万tokens")
    print("  2. Kimi（中文优化）- 128k上下文，中文最好")
    print("  3. Gemini（免费）- 每天1500次免费请求")
    print()

    llm_choice = input("请选择分析师（输入1-3）: ").strip()

    # 映射到配置
    analyst_configs = {
        "1": {"name": "DeepSeek", "provider": "openai", "url": "https://api.deepseek.com/v1",
              "model": "deepseek-chat", "api_key": api_keys.get("deepseek", "")},
        "2": {"name": "Kimi", "provider": "openai", "url": "https://api.moonshot.cn/v1",
              "model": "moonshot-v1-8k", "api_key": api_keys.get("kimi", "")},
        "3": {"name": "Gemini", "provider": "google",
              "model": "gemini-2.5-flash", "api_key": api_keys.get("gemini", "")}
    }

    config = analyst_configs.get(llm_choice)
    if not config:
        print("[错误] 无效选择")
        input("按回车键退出...")
        sys.exit(1)

    if not config.get("api_key"):
        print(f"[错误] {config['name']} 的API密钥未找到")
        print(f"[提示] 请在 {LLM_API_FILE} 中添加密钥")
        input("按回车键退出...")
        sys.exit(1)

    print(f"[已确认] 您选择了 {config['name']} 分析师")
    print()

    # 步骤2：输入股票代码
    print("=" * 80)
    print()
    print("常用股票代码:")
    print("  - 美股: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN")
    print("  - 中概股: BABA, JD, PDD, BIDU")
    print("  - 加密货币: BTC-USD, ETH-USD")
    print()

    ticker = input("请输入股票代码: ").strip().upper()
    print()

    # 步骤3：输入日期范围
    print("=" * 80)
    print()
    print("系统将根据开始日期自动选择数据源:")
    print()
    print("  - 开始日期 ≤ 2024-12-31: 使用 WRDS 学术数据库 ⭐")
    print("  - 开始日期 > 2024-12-31: 使用实时数据（Alpha Vantage）")
    print()
    print("日期范围示例:")
    print("  - 开始: 2024-06-15, 结束: 2024-08-15（使用WRDS，2个月）")
    print("  - 开始: 2025-01-15, 结束: 2025-03-20（实时数据，2个月）")
    print()

    start_date = input("请输入开始日期（格式: YYYY-MM-DD）: ").strip()
    end_date = input("请输入结束日期（格式: YYYY-MM-DD，留空使用今天）: ").strip()

    if end_date == "":
        end_date = datetime.now().strftime("%Y-%m-%d")
        print(f"[默认] 使用今天作为结束日期: {end_date}")

    print()
    print(f"[已确认] 分析日期范围: {start_date} 到 {end_date}")

    # 计算天数
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days
        print(f"[计算] 分析周期: {days} 天")
    except ValueError as e:
        print(f"[错误] 日期格式错误: {e}")
        input("按回车键退出...")
        sys.exit(1)

    print()

    # 步骤4：选择分析类型
    print("=" * 80)
    print()
    print("可用分析类型:")
    print("  1. 完整分析（推荐）")
    print("     ✓ 技术面分析（技术指标、趋势）")
    print("     ✓ 基本面分析（财务数据、估值）")
    print("     ✓ 情绪面分析（新闻情感、市场情绪）")
    print("     ✓ 投资建议和风险评估")
    print()
    print("  2. 快速分析")
    print("     ✓ 技术面分析")
    print("     ✓ 基本面分析")
    print()
    print("  3. 情绪分析")
    print("     ✓ 新闻情绪分析")
    print("     ✓ 市场情绪评估")
    print()

    analysis_type = input("请选择分析类型（输入1-3，默认1）: ").strip()

    if not analysis_type:
        analysis_type = "1"

    analysis_names = {
        "1": "完整分析",
        "2": "快速分析",
        "3": "情绪分析"
    }

    analysis_name = analysis_names.get(analysis_type, "完整分析")
    print(f"[已确认] 分析类型: {analysis_name}")
    print()

    # 步骤5：开始分析
    print("=" * 80)
    print()
    print("开始分析系统...")
    print()

    try:
        # 导入TradingAgents框架
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        from intelligent_data_fetcher import IntelligentDataFetcher

        # 配置TradingAgents
        trade_config = DEFAULT_CONFIG.copy()

        # 设置LLM配置
        if config["provider"] == "openai":
            trade_config["llm_provider"] = "openai"
            trade_config["backend_url"] = config["url"]
            trade_config["deep_think_llm"] = config["model"]
            trade_config["quick_think_llm"] = config["model"]
            os.environ["OPENAI_API_KEY"] = config["api_key"]
        elif config["provider"] == "google":
            trade_config["llm_provider"] = "google"
            trade_config["deep_think_llm"] = config["model"]
            os.environ["GOOGLE_API_KEY"] = config["api_key"]

        trade_config["output_language"] = "Chinese"

        # 根据日期选择数据源
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        cutoff_dt = datetime(2024, 12, 31)

        if start_dt <= cutoff_dt:
            print(f"[数据源] 使用 WRDS 学术数据库（适用于 {start_date}）⭐")
            trade_config["data_vendors"] = {
                "core_stock_apis": "wrds",
                "fallback_apis": "alpha_vantage"
            }
        else:
            print(f"[数据源] 使用 Alpha Vantage API（适用于 {start_date}）")
            trade_config["data_vendors"] = {
                "core_stock_apis": "alpha_vantage",
                "fallback_apis": "yfinance"
            }

        # 根据分析类型调整
        if analysis_type == "3":
            trade_config["max_debate_rounds"] = 1
            trade_config["max_risk_discuss_rounds"] = 1
        elif analysis_type == "1":
            trade_config["max_debate_rounds"] = 2
            trade_config["max_risk_discuss_rounds"] = 2

        print()
        print(f"[启动] 正在初始化 {config['name']} 分析引擎...")

        # 初始化TradingAgents
        ta = TradingAgentsGraph(debug=True, config=trade_config)

        print()
        print(f"[分析] 正在分析 {ticker}（分析周期: {start_date} 到 {end_date}）...")
        print(f"[基准] 以 {end_date} 为分析基准日")
        print()

        # 运行分析
        _, decision = ta.propagate(ticker, end_date)

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
        import traceback
        traceback.print_exc()
        print()

    input("按回车键退出...")


if __name__ == "__main__":
    main()
