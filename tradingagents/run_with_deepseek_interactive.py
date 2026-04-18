"""
使用 DeepSeek API 运行 TradingAgents 的交互式脚本

配置说明：
1. DeepSeek API 已配置
2. 模型使用 deepseek-chat
3. 数据源使用 yfinance

使用方法：
python run_with_deepseek_interactive.py
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.smart_router import get_smart_config

# 加载环境变量
load_dotenv()

# 强制使用 DeepSeek API Key（覆盖系统环境变量）
DEEPSEEK_API_KEY = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"
os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY

print("="*70)
print("           TradingAgents - 交互式股票分析")
print("="*70)
print()

# 显示常用资产代码
print("常用资产代码参考：")
print()
print("₿ 加密货币（新支持！）：")
print("  BTC    - 比特币 (Bitcoin)")
print("  ETH    - 以太坊 (Ethereum)")
print("  BNB    - 币安币 (Binance Coin)")
print("  SOL    - Solana")
print("  XRP    - 瑞波币 (XRP)")
print()
print("🇺🇸 美股科技股：")
print("  AAPL   - 苹果")
print("  TSLA   - 特斯拉")
print("  NVDA   - 英伟达")
print("  MSFT   - 微软")
print("  GOOGL  - 谷歌")
print()
print("🇨🇳 中概股：")
print("  BABA   - 阿里巴巴")
print("  JD     - 京东")
print("  BIDU   - 百度")
print("  PDD    - 拼多多")
print()
print("港股：")
print("  0700.HK  - 腾讯控股")
print("  9988.HK  - 阿里巴巴港股")
print()
print("A股：")
print("  600519.SS - 贵州茅台")
print("  000001.SZ - 平安银行")
print()
print("="*70)
print()

# 让用户输入股票代码
ticker = input("请输入股票代码（如 AAPL, BABA, 0700.HK）: ").strip()

if not ticker:
    print("[错误] 股票代码不能为空")
    input("按 Enter 键退出...")
    exit(1)

# 让用户输入日期
print()
date = input("请输入分析日期（如 2025-01-15，留空使用今天）: ").strip()

if not date:
    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")
    print(f"[INFO] 使用今天日期: {date}")

print()
print("="*70)
print(f"开始分析: {ticker}")
print(f"分析日期: {date}")
print("="*70)
print()

# 配置 TradingAgents 使用 DeepSeek
config = DEFAULT_CONFIG.copy()

# DeepSeek 配置（使用 OpenAI 兼容模式）
config["llm_provider"] = "openai"  # DeepSeek 兼容 OpenAI 格式
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"      # 深度思考模型
config["quick_think_llm"] = "deepseek-chat"     # 快速任务模型

# 输出语言设置为中文
config["output_language"] = "Chinese"

# 辩论轮数（降低可以节省 API 调用）
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 数据源配置
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",
}

# 智能数据源路由 - 自动检测A股并使用efinance
config = get_smart_config(ticker, config)

print("[INFO] 初始化 TradingAgents（使用 DeepSeek）...")
print("[INFO] 多智能体分析系统启动中...")
print()

# 显示智能体列表
print("智能体包括：")
print("  ✓ 基本面分析师 - 分析公司财务")
print("  ✓ 情绪分析师 - 分析市场情绪")
print("  ✓ 新闻分析师 - 分析相关新闻")
print("  ✓ 技术分析师 - 分析技术指标")
print("  ✓ 研究员团队 - 辩论分析")
print("  ✓ 交易员 - 制定交易策略")
print("  ✓ 风险管理团队 - 评估风险")
print("  ✓ 投资组合经理 - 最终决策")
print()
print("请稍候，这可能需要几分钟...")
print()

try:
    # 创建 TradingAgents 实例
    ta = TradingAgentsGraph(debug=True, config=config)

    # 运行分析
    _, decision = ta.propagate(ticker, date)

    print()
    print("="*70)
    print("=== 最终交易决策 ===")
    print("="*70)
    print()
    print(decision)
    print()
    print("="*70)
    print()

    print("[OK] 分析完成！")

except Exception as e:
    print()
    print("="*70)
    print(f"[ERROR] 分析失败: {e}")
    print("="*70)
    print()
    print("可能的原因：")
    print("1. 股票代码不正确（注意区分大小写）")
    print("2. yfinance 无法获取该股票数据")
    print("3. 网络连接问题")
    print("4. API 余额不足")
    print()
    print("建议：")
    print("• 检查股票代码格式（如：AAPL, BABA, 0700.HK）")
    print("• 尝试其他股票代码")
    print("• 确认网络连接正常")
    print()
    print("股票代码格式参考：")
    print("  美股: AAPL, TSLA, NVDA")
    print("  中概股: BABA, JD, BIDU")
    print("  港股: 0700.HK, 9988.HK")
    print("  A股: 600519.SS, 000001.SZ")
    print()

print()
input("按 Enter 键退出...")
