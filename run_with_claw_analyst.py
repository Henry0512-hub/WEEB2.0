"""
使用 Claw 新闻分析师运行 TradingAgents

Claw 新闻分析师使用 crawl4ai 爬取中国新闻网站，
提供中国财经市场的实时新闻分析。
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 加载环境变量
load_dotenv()

# 检查 API 密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[错误] 未找到 OPENAI_API_KEY")
    print("请在 .env 文件中设置")
    exit(1)

print(f"[OK] DeepSeek API Key 已加载: {api_key[:10]}...{api_key[-4:]}")

# 配置 TradingAgents
config = DEFAULT_CONFIG.copy()

# 使用 DeepSeek
config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"

# 输出语言设置为中文
config["output_language"] = "Chinese"

# 降低辩论轮数
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 数据源配置
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",  # 主新闻源还是用 yfinance
}

print("\n=== TradingAgents + Claw 新闻分析师 ===")
print(f"LLM Provider: {config['llm_provider']}")
print(f"模型: {config['deep_think_llm']}")
print(f"输出语言: {config['output_language']}")
print(f"新闻源: yfinance + Claw (中国新闻爬虫)")

# 创建 TradingAgents 实例
print("\n[INFO] 初始化 TradingAgents...")
print("[INFO] Claw 新闻分析师将提供中国财经新闻")

ta = TradingAgentsGraph(debug=True, config=config)

# 示例：分析中概股
print("\n=== 开始股票分析 ===")

print("\n推荐的中概股：")
print("- BABA: 阿里巴巴")
print("- JD: 京东")
print("- BIDU: 百度")
print("- NTES: 网易")
print("- PDD: 拼多多")

ticker = "BABA"  # 阿里巴巴
date = "2025-01-15"

print(f"\n股票代码: {ticker}")
print(f"分析日期: {date}")

print("\n[INFO] 正在启动多智能体分析系统...")
print("智能体包括：")
print("  - 基本面分析师")
print("  - 情绪分析师")
print("  - 新闻分析师 (yfinance)")
print("  - Claw 新闻分析师 (中国新闻爬虫) ⭐ 新增")
print("  - 技术分析师")
print("  - 研究员团队")
print("  - 交易员")
print("  - 风险管理团队")
print("  - 投资组合经理")

print("\n请稍候，Claw 正在爬取中国新闻...\n")

try:
    # 运行分析
    _, decision = ta.propagate(ticker, date)

    print("\n" + "="*60)
    print("=== 最终交易决策 ===")
    print("="*60)
    print(decision)
    print("="*60)

    print("\n[OK] 分析完成！")
    print("\nClaw 新闻分析师提供的独特价值：")
    print("✓ 实时爬取中国财经新闻")
    print("✓ 覆盖央视、新浪财经、东方财富等本土源")
    print("✓ 提供中国市场独特视角")
    print("✓ 补充 yfinance 的中国新闻覆盖不足")

except Exception as e:
    print(f"\n[ERROR] 分析失败: {e}")
    print("\n可能的原因：")
    print("1. Claw 爬虫初始化失败")
    print("2. 网站结构变化导致爬取失败")
    print("3. 网络连接问题")
    print("\n建议：")
    print("查看 claw_news_crawler.py 的日志")

# Claw 使用说明
print("\n=== Claw 新闻分析师使用说明 ===")
print("\n什么是 Claw？")
print("Claw 是一个基于 crawl4ai 的新闻爬虫，专门用于获取中国财经新闻")

print("\nClaw 支持的新闻源：")
print("- 央视网 (CCTV)")
print("- 新浪财经")
print("- 东方财富")
print("- 证券时报")
print("- 第一财经")

print("\nClaw 的优势：")
print("✓ 实时性：直接爬取网站，最新新闻")
print("✓ 全面性：覆盖多个中国财经媒体")
print("✓ 本土化：中国市场的独特视角")
print("✓ 免费开源：无需 API Key")

print("\nClaw 与其他新闻源对比：")
print("- yfinance: 国际新闻，适合美股")
print("- Alpha Vantage: 全球新闻，有请求限制")
print("- Claw: 中国新闻，实时爬取，无限制")

print("\n如何使用 Claw：")
print("1. 单独测试 Claw：")
print("   python claw_news_crawler.py")
print("\n2. 集成到 TradingAgents：")
print("   python run_with_claw_analyst.py")
print("\n3. 在代码中调用：")
print("   from claw_news_crawler import crawl_chinese_news_sync")
print("   news = crawl_chinese_news_sync()")

print("\n注意事项：")
print("- Claw 需要网络连接到目标网站")
print("- 首次运行会下载浏览器（playwright）")
print("- 爬取速度取决于网络和网站响应速度")
print("- 请遵守网站的 robots.txt 和使用条款")
