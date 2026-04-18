"""
使用 Gemini API 运行 TradingAgents

免费额度：每天 1,500 次请求
模型：Gemini 2.5 Flash（快速、强大）
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 加载环境变量
load_dotenv()

# 检查 API 密钥
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("[错误] 未找到 GOOGLE_API_KEY")
    print("请在 .env 文件中设置：GOOGLE_API_KEY=your-key")
    exit(1)

print(f"[OK] Gemini API Key 已加载: {api_key[:10]}...{api_key[-4:]}")

# 配置 TradingAgents 使用 Gemini
config = DEFAULT_CONFIG.copy()

# Gemini 配置
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.5-flash"        # 主要推理模型（免费）
config["quick_think_llm"] = "gemini-2.5-flash-lite"  # 快速任务模型

# 可选：使用更强的模型（也在免费额度内）
# config["deep_think_llm"] = "gemini-2.5-pro"

# 输出语言
config["output_language"] = "Chinese"

# 降低辩论轮数以节省 API 调用
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 数据源配置
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",
}

print("\n=== TradingAgents 配置 ===")
print(f"LLM Provider: {config['llm_provider']}")
print(f"Deep Think Model: {config['deep_think_llm']}")
print(f"Quick Think Model: {config['quick_think_llm']}")
print(f"Output Language: {config['output_language']}")

# 创建 TradingAgents 实例
print("\n[INFO] 初始化 TradingAgents（使用 Gemini）...")
ta = TradingAgentsGraph(debug=True, config=config)

# 示例：分析股票
print("\n=== 开始股票分析 ===")

# 推荐的股票代码示例
print("\n支持的股票代码示例：")
print("美股: AAPL, TSLA, NVDA, BABA, BIDU")
print("港股: 0700.HK (腾讯), 9988.HK (阿里巴巴)")
print("A股: 600519.SS (茅台), 000001.SZ (平安)")

ticker = "AAPL"  # 苹果公司
date = "2025-01-15"

print(f"\n股票代码: {ticker}")
print(f"分析日期: {date}")

print("\n[INFO] 正在启动多智能体分析系统...")
print("智能体包括：")
print("  - 基本面分析师")
print("  - 情绪分析师")
print("  - 新闻分析师")
print("  - 技术分析师")
print("  - 研究员团队")
print("  - 交易员")
print("  - 风险管理团队")
print("  - 投资组合经理")

print("\n请稍候，这可能需要几分钟...\n")

try:
    # 运行分析
    _, decision = ta.propagate(ticker, date)

    print("\n" + "="*60)
    print("=== 最终交易决策 ===")
    print("="*60)
    print(decision)
    print("="*60)

    print("\n[OK] 分析完成！")
    print("\n[提示] Gemini 免费额度: 每天 1,500 次请求")

except Exception as e:
    print(f"\n[ERROR] 分析失败: {e}")
    print("\n可能的原因：")
    print("1. 网络无法访问 Google（需要科学上网）")
    print("2. API Key 无效")
    print("3. 超出免费额度限制")
    print("\n建议：")
    print("如果无法访问 Google，可以使用 DeepSeek 作为替代")
    print("修改配置: config['llm_provider'] = 'deepseek'")

# 使用说明
print("\n=== Gemini API 使用说明 ===")
print("✅ 免费额度: 每天 1,500 次请求")
print("✅ 模型: Gemini 2.5 Flash（最新）")
print("✅ 速度: 非常快")
print("✅ 能力: 推理能力强，适合金融分析")

print("\n其他可用模型：")
print("- gemini-2.5-flash: 推荐，平衡速度和质量")
print("- gemini-2.5-flash-lite: 更轻量，更快")
print("- gemini-2.5-pro: 更强推理能力")

print("\n网络要求：")
print("- 需要能访问 Google API")
print("- 如果无法访问，建议使用 DeepSeek")

print("\n替换方案：")
print("如果 Gemini 无法使用，修改 .env 文件：")
print("  注释掉 GOOGLE_API_KEY")
print("  确保 OPENAI_API_KEY 指向 DeepSeek API")
