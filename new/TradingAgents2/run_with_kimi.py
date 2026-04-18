"""
使用 Kimi API 运行 TradingAgents

Kimi (月之暗面) - 国产大模型
优势：中文支持好，128k 长上下文，稳定可靠
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 加载环境变量
load_dotenv()

# 检查 API 密钥
api_key = os.getenv("KIMI_API_KEY")
if not api_key:
    print("[错误] 未找到 KIMI_API_KEY")
    print("请在 .env 文件中设置：KIMI_API_KEY=your-key")
    exit(1)

print(f"[OK] Kimi API Key 已加载: {api_key[:10]}...{api_key[-4:]}")

# 配置 TradingAgents 使用 Kimi
config = DEFAULT_CONFIG.copy()

# Kimi 配置（使用 OpenAI 兼容模式）
config["llm_provider"] = "openai"  # Kimi 兼容 OpenAI 格式
config["backend_url"] = "https://api.moonshot.cn/v1"
config["deep_think_llm"] = "moonshot-v1-8k"      # 主要推理模型
config["quick_think_llm"] = "moonshot-v1-8k"     # 快速任务模型

# 可选：使用更强的模型
# config["deep_think_llm"] = "moonshot-v1-32k"   # 32k 上下文
# config["deep_think_llm"] = "moonshot-v1-128k"  # 128k 上下文

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
print(f"LLM Provider: Kimi (Moonshot AI)")
print(f"Backend URL: {config['backend_url']}")
print(f"Deep Think Model: {config['deep_think_llm']}")
print(f"Output Language: {config['output_language']}")

# 创建 TradingAgents 实例
print("\n[INFO] 初始化 TradingAgents（使用 Kimi）...")

# 设置 API Key
os.environ["OPENAI_API_KEY"] = api_key

ta = TradingAgentsGraph(debug=True, config=config)

# 示例：分析股票
print("\n=== 开始股票分析 ===")

print("\n支持的股票代码示例：")
print("美股: AAPL, TSLA, NVDA, BABA, BIDU")
print("港股: 0700.HK (腾讯), 9988.HK (阿里巴巴)")
print("A股: 600519.SS (茅台), 000001.SZ (平安)")

ticker = "TSLA"  # 特斯拉
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

except Exception as e:
    print(f"\n[ERROR] 分析失败: {e}")
    print("\n可能的原因：")
    print("1. API Key 无效")
    print("2. 网络连接问题")
    print("3. API 余额不足")

# Kimi API 说明
print("\n=== Kimi API 使用说明 ===")
print("提供商：月之暗面 (Moonshot AI)")
print("官网：https://www.moonshot.cn/")
print("优势：")
print("  - 中文支持优秀")
print("  - 128k 长上下文")
print("  - 稳定可靠")
print("  - 国内可直接访问")

print("\n可用模型：")
print("- moonshot-v1-8k: 8k 上下文（推荐）")
print("- moonshot-v1-32k: 32k 上下文")
print("- moonshot-v1-128k: 128k 上下文（最长）")

print("\n价格：")
print("请访问 https://platform.moonshot.cn/console 查看价格")

print("\n获取 API Key：")
print("1. 访问：https://platform.moonshot.cn/console")
print("2. 注册账号")
print("3. 创建 API Key")
print("4. 复制到 .env 文件的 KIMI_API_KEY")
