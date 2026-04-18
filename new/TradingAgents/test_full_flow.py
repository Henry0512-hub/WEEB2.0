# -*- coding: utf-8 -*-
"""
测试完整的加密货币分析流程
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
    print(f"[配置] API密钥已加载")
except ImportError:
    print("[警告] 使用默认密钥")

from tradingagents.dataflows.smart_router import get_smart_config
from tradingagents.default_config import DEFAULT_CONFIG

print("="*70)
print("完整流程测试")
print("="*70)
print()

# 测试币种
test_ticker = "ETH"

print(f"[步骤1] 测试币种: {test_ticker}")
print()

print("[步骤2] 获取默认配置...")
config = DEFAULT_CONFIG.copy()
print(f"默认data_vendors: {config.get('data_vendors', {})}")
print()

print("[步骤3] 应用智能路由...")
config = get_smart_config(test_ticker, config)
print(f"路由后data_vendors: {config.get('data_vendors', {})}")
print()

print("[步骤4] 测试数据获取...")
from tradingagents.dataflows.interface import route_to_vendor

try:
    # 测试获取价格数据
    from datetime import datetime
    end_date = datetime.now()
    start_date = end_date

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"获取 {test_ticker} 数据 ({start_str} 到 {end_str})...")

    result = route_to_vendor("get_stock_data", test_ticker, start_str, end_str)

    print()
    print("[成功] 数据获取成功!")
    print()
    print("数据预览（前500字符）:")
    print("-"*70)
    print(result[:500])
    print("-"*70)

except Exception as e:
    print()
    print(f"[失败] {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("测试完成")
print("="*70)
