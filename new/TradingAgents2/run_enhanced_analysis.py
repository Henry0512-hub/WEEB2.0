"""
增强版分析脚本 - 包含技术面、基本面、情绪面分析
支持根据日期自动选择数据源
智能降级：yfinance限流时自动使用Claw爬虫
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入智能数据获取器
from intelligent_data_fetcher import IntelligentDataFetcher

def get_analyst_config(choice):
    """根据选择返回分析师配置"""
    configs = {
        "1": {
            "name": "DeepSeek",
            "provider": "openai",
            "url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "api_key": "sk-d28ae30a58cb496c9b40e0029d0ef2c1",
            "script": "run_with_deepseek.py"
        },
        "2": {
            "name": "Kimi",
            "provider": "openai",
            "url": "https://api.moonshot.cn/v1",
            "model": "moonshot-v1-8k",
            "api_key": "sk-PBksAJzkTW48yH12moqKci3hckekib80qJzMz63MG4XVfPyd",
            "script": "run_with_kimi.py"
        },
        "3": {
            "name": "Gemini",
            "provider": "google",
            "model": "gemini-2.5-flash",
            "api_key": "AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk",
            "script": "run_with_gemini.py"
        }
    }
    return configs.get(choice)

def should_use_wrds(date_str):
    """判断是否应该使用WRDS"""
    try:
        analysis_date = datetime.strptime(date_str, "%Y-%m-%d")
        cutoff_date = datetime(2024, 12, 31)
        return analysis_date <= cutoff_date
    except:
        return False

def get_analysis_info(ticker, start_date, end_date, analyst_name, use_wrds, analysis_type):
    """生成分析信息"""
    # 计算天数
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days
        days_str = f"{days} 天"
    except:
        days_str = "自动计算"

    info = f"""
{'='*70}
TradingAgents 增强分析系统
{'='*70}

分析配置:
  股票代码:      {ticker}
  分析日期范围:  {start_date} 到 {end_date}
  分析周期:      {days_str}
  分析师:        {analyst_name}
  分析类型:      {analysis_type}

数据源:
"""

    if use_wrds:
        info += f"  - WRDS 学术数据库 (历史数据)\n"
        info += f"  - yfinance (价格数据)\n"
        info += f"  - 新闻源 (历史新闻)\n"
    else:
        info += f"  - yfinance (实时数据)\n"
        info += f"  - 实时新闻源\n"
        info += f"  - 财务数据 (基本面)\n"

    info += f"\n分析模块:\n"

    if analysis_type == "1":
        info += f"  ✓ 技术面分析 (技术指标、趋势)\n"
        info += f"  ✓ 基本面分析 (财务数据、估值)\n"
        info += f"  ✓ 情绪面分析 (新闻情感、市场情绪)\n"
        info += f"  ✓ 综合投资建议\n"
    elif analysis_type == "2":
        info += f"  ✓ 技术面分析\n"
        info += f"  ✓ 基本面分析\n"
    else:  # analysis_type == "3"
        info += f"  ✓ 情绪面分析\n"
        info += f"  ✓ 市场情绪评估\n"

    info += f"\n{'='*70}\n"

    return info

def main():
    """主函数"""

    if len(sys.argv) < 5:
        print("用法: python run_enhanced_analysis.py <股票代码> <开始日期> <结束日期> <分析师选择> <分析类型>")
        print("示例: python run_enhanced_analysis.py AAPL 2024-06-15 2024-08-15 1 1")
        print()
        print("参数说明:")
        print("  股票代码: AAPL, TSLA, NVDA 等")
        print("  开始日期: YYYY-MM-DD 格式")
        print("  结束日期: YYYY-MM-DD 格式")
        print("  分析师: 1=DeepSeek, 2=Kimi, 3=Gemini")
        print("  分析类型: 1=完整分析, 2=快速分析, 3=情绪分析")
        print()
        print("示例:")
        print("  python run_enhanced_analysis.py AAPL 2024-06-15 2024-08-15 1 1")
        print("  python run_enhanced_analysis.py TSLA 2025-01-15 2025-03-20 2 1")
        print("  python run_enhanced_analysis.py NVDA 2025-03-01 2025-04-09 3 3")
        sys.exit(1)

    ticker = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    analyst_choice = sys.argv[4]
    analysis_type = sys.argv[5] if len(sys.argv) > 5 else "1"

    # 验证日期格式
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if start_dt > end_dt:
            print(f"[错误] 开始日期不能晚于结束日期")
            sys.exit(1)

        days = (end_dt - start_dt).days
        print(f"[验证] 分析周期: {days} 天")

    except ValueError as e:
        print(f"[错误] 日期格式错误: {e}")
        print("请使用 YYYY-MM-DD 格式")
        sys.exit(1)

    # 获取分析师配置
    config = get_analyst_config(analyst_choice)
    if not config:
        print(f"[错误] 无效的分析师选择: {analyst_choice}")
        sys.exit(1)

    # 判断数据源（基于开始日期）
    use_wrds = should_use_wrds(start_date)

    # 设置API密钥
    if config["provider"] == "openai":
        os.environ["OPENAI_API_KEY"] = config["api_key"]
    elif config["provider"] == "google":
        os.environ["GOOGLE_API_KEY"] = config["api_key"]

    # 显示分析信息
    analysis_type_names = {
        "1": "完整分析",
        "2": "快速分析",
        "3": "情绪分析"
    }

    print(get_analysis_info(
        ticker, start_date, end_date, config["name"], use_wrds, analysis_type_names.get(analysis_type, "完整分析")
    ))

    # 智能数据获取（自动降级）
    print(f"\n{'='*70}")
    print(f"智能数据获取系统")
    print(f"{'='*70}")
    print(f"\n策略:")
    print(f"  1. yfinance API (最快)")
    print(f"  2. Claw 爬虫 (互联网爬取)")
    print(f"  3. 模拟数据 (备选)")
    print()

    try:
        fetcher = IntelligentDataFetcher(ticker, start_date, end_date)
        stock_data, data_source = fetcher.fetch_stock_data()

        print(f"\n[数据摘要]")
        print(fetcher.get_data_summary(stock_data))

        # 保存数据供 TradingAgents 使用
        import tempfile
        import json

        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump({
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'source': data_source,
            'data': stock_data.to_dict()
        }, data_file.name)
        data_file.close()

        print(f"[数据] 已保存到临时文件: {data_file.name}\n")

    except Exception as e:
        print(f"\n[警告] 智能数据获取失败: {e}")
        print(f"[继续] 将使用 TradingAgents 内置数据源\n")
        data_file = None

    # 导入并运行TradingAgents
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # 配置TradingAgents
        trade_config = DEFAULT_CONFIG.copy()

        if config["provider"] == "openai":
            trade_config["llm_provider"] = "openai"
            trade_config["backend_url"] = config["url"]
            trade_config["deep_think_llm"] = config["model"]
            trade_config["quick_think_llm"] = config["model"]
        elif config["provider"] == "google":
            trade_config["llm_provider"] = "google"
            trade_config["deep_think_llm"] = config["model"]

        trade_config["output_language"] = "Chinese"

        # 根据日期选择数据源
        if use_wrds:
            print(f"[数据源] 使用 WRDS 学术数据库 (适用于 {start_date})")
            trade_config["data_vendors"] = {
                "core_stock_apis": "wrds",
                "fallback_apis": "alpha_vantage"
            }
        else:
            print(f"[数据源] 使用 Alpha Vantage API (适用于 {start_date})")
            trade_config["data_vendors"] = {
                "core_stock_apis": "alpha_vantage",
                "fallback_apis": "yfinance"
            }

        # 根据分析类型调整
        if analysis_type == "3":
            # 情绪分析：减少辩论轮数，更快
            trade_config["max_debate_rounds"] = 1
            trade_config["max_risk_discuss_rounds"] = 1
        elif analysis_type == "1":
            # 完整分析：增加深度
            trade_config["max_debate_rounds"] = 2
            trade_config["max_risk_discuss_rounds"] = 2

        print(f"\n[启动] 正在初始化 {config['name']} 分析引擎...")
        ta = TradingAgentsGraph(debug=True, config=trade_config)

        print(f"\n[分析] 正在分析 {ticker} (分析周期: {start_date} 到 {end_date})...")
        print(f"[基准] 以 {end_date} 为分析基准日")
        print()

        # 运行分析（使用结束日期作为分析基准日）
        _, decision = ta.propagate(ticker, end_date)

        print(f"\n{'='*70}")
        print(f"分析完成！")
        print(f"{'='*70}")
        print(f"\n{decision}\n")

    except Exception as e:
        print(f"\n[错误] 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
