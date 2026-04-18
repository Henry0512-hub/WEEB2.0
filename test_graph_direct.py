# -*- coding: utf-8 -*-
"""
直接测试TradingAgentsGraph调用
找出404错误的真正原因
"""
import sys
sys.path.append('C:\\Users\\lenovo\\TradingAgents')

import os
from dotenv import load_dotenv

# 加载API密钥
load_dotenv()
try:
    from api_config import DEEPSEEK_API_KEY
    os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY
except:
    pass

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.smart_router import get_smart_config
from datetime import datetime

print("="*70)
print("TradingAgentsGraph 直接测试")
print("="*70)
print()

# 测试参数
ticker = "ETH"
date = datetime.now().strftime("%Y-%m-%d")

print(f"测试参数:")
print(f"  币种: {ticker}")
print(f"  日期: {date}")
print()

# 配置
config = DEFAULT_CONFIG.copy()

# DeepSeek配置
config["llm_provider"] = "openai"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"
config["output_language"] = "Chinese"

# 降低辩论轮数以节省API
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 数据源配置
config["data_vendors"] = {
    "core_stock_apis": "coingecko",
    "technical_indicators": "yfinance",
    "fundamental_data": "coingecko",
    "news_data": "yfinance",
}

# 应用智能路由
config = get_smart_config(ticker, config)

print("配置信息:")
print(f"  LLM提供商: {config['llm_provider']}")
print(f"  模型: {config['deep_think_llm']}")
print(f"  数据源: {config['data_vendors']}")
print()

try:
    print("[启动] 创建TradingAgents实例...")
    ta = TradingAgentsGraph(debug=True, config=config)

    print("[运行] 开始分析...")
    print()
    print("="*70)

    # 运行分析
    final_state, decision = ta.propagate(ticker, date)

    print()
    print("="*70)
    print("[成功] 分析完成!")
    print()
    print("最终决策:")
    print(decision)

except Exception as e:
    print()
    print("="*70)
    print(f"[错误] 分析失败: {e}")
    print("="*70)
    print()
    print("错误详情:")
    import traceback
    traceback.print_exc()
