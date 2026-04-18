"""
使用 DeepSeek API 运行 TradingAgents 的示例脚本

配置说明：
1. DeepSeek API 已配置在 .env 文件中
2. 模型使用 deepseek-chat（性价比高）
3. 数据源使用 yfinance（免费）

使用方法：
python run_with_deepseek.py
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 加载环境变量
load_dotenv()

# 强制使用 DeepSeek API Key（覆盖系统环境变量）
DEEPSEEK_API_KEY = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"
os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY

# 确认 API 密钥
api_key = DEEPSEEK_API_KEY
print(f"[OK] DeepSeek API Key 已设置: {api_key[:10]}...{api_key[-4:]}")

# 配置 TradingAgents 使用 DeepSeek
config = DEFAULT_CONFIG.copy()

# DeepSeek 配置（使用 OpenAI 兼容模式）
config["llm_provider"] = "openai"  # DeepSeek 兼容 OpenAI 格式
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"      # 深度思考模型
config["quick_think_llm"] = "deepseek-chat"     # 快速任务模型

# 可选：使用 DeepSeek-R1（推理优化模型）
# config["deep_think_llm"] = "deepseek-reasoner"

# 输出语言设置为中文
config["output_language"] = "Chinese"

config["max_debate_rounds"] = 3
config["max_risk_discuss_rounds"] = 3
config["max_recur_limit"] = 200

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
print(f"Backend URL: {config['backend_url']}")
print(f"Output Language: {config['output_language']}")

# 创建 TradingAgents 实例
print("\n[INFO] 初始化 TradingAgents...")
ta = TradingAgentsGraph(debug=True, config=config)

# 示例：分析一只股票
print("\n=== 开始股票分析 ===")

# 中国股票示例（需要使用 yfinance 代码）
# 贵州茅台: 600519.SS
# 腾讯控股: 0700.HK
# 阿里巴巴: BABA
# 百度: BIDU

ticker = "BABA"  # 阿里巴巴
date = "2025-01-15"

print(f"股票代码: {ticker}")
print(f"分析日期: {date}")
print(f"数据源: yfinance")

print("\n[INFO] 正在启动多智能体分析系统...")
print("  - 基本面分析师")
print("  - 情绪分析师")
print("  - 新闻分析师")
print("  - 技术分析师")
print("  - 研究员（看多/看空）")
print("  - 交易员")
print("  - 风险管理团队")
print("  - 投资组合经理")

print("\n请耐心等待，这可能需要几分钟...\n")

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
    print("\n提示：")
    print("1. 检查网络连接")
    print("2. 确认 API 密钥有效")
    print("3. 尝试更换股票代码或日期")
    raise

# 使用建议
print("\n=== 使用建议 ===")
print("1. 降低辩论轮数可节省 API 调用")
print("2. 中国股票代码格式：")
print("   - 上海证券交易所: 600519.SS")
print("   - 深圳证券交易所: 000001.SZ")
print("   - 香港交易所: 0700.HK")
print("   - 美股中概股: BABA, BIDU, JD 等")
print("3. 分析日期建议使用最近的交易日")
print("4. DeepSeek API 性价比高，适合高频使用")
