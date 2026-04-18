"""
DeepSeek API 配置示例
用于 TradingAgents 框架
"""

from tradingagents.default_config import DEFAULT_CONFIG

# DeepSeek API 配置
DEEPSEEK_CONFIG = DEFAULT_CONFIG.copy()

# LLM 提供商设置为 deepseek（兼容 OpenAI 格式）
DEEPSEEK_CONFIG["llm_provider"] = "deepseek"

# 设置 DeepSeek API base URL
DEEPSEEK_CONFIG["backend_url"] = "https://api.deepseek.com/v1"

# 设置 DeepSeek 模型
DEEPSEEK_CONFIG["deep_think_llm"] = "deepseek-chat"      # 主要推理模型
DEEPSEEK_CONFIG["quick_think_llm"] = "deepseek-chat"     # 快速任务模型

# 可选：使用 DeepSeek-R1 作为深度推理模型
# DEEPSEEK_CONFIG["deep_think_llm"] = "deepseek-reasoner"

# 其他配置保持默认
DEEPSEEK_CONFIG["max_debate_rounds"] = 1
DEEPSEEK_CONFIG["max_risk_discuss_rounds"] = 1
DEEPSEEK_CONFIG["output_language"] = "Chinese"  # 输出中文

# 数据源配置（使用 akshare 或 yfinance）
DEEPSEEK_CONFIG["data_vendors"] = {
    "core_stock_apis": "yfinance",        # 可以改为 "akshare"
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",
}

# 使用示例
if __name__ == "__main__":
    import os

    # 设置 DeepSeek API 密钥（请替换为你的实际密钥）
    os.environ["OPENAI_API_KEY"] = "your-deepseek-api-key-here"
    # 或者使用环境变量
    # os.environ["DEEPSEEK_API_KEY"] = "your-deepseek-api-key-here"

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    # 创建 TradingAgents 实例
    ta = TradingAgentsGraph(debug=True, config=DEEPSEEK_CONFIG)

    # 运行分析（示例：分析贵州茅台 2025-01-15）
    ticker = "600519.SS"  # 贵州茅台在上海证券交易所的代码
    date = "2025-01-15"

    _, decision = ta.propagate(ticker, date)
    print(f"\n=== 最终决策 ===")
    print(decision)
