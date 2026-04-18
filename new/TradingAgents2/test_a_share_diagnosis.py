"""
A股数据源诊断脚本
用于测试和诊断A股数据获取问题
"""

import sys
sys.path.insert(0, 'C:/Users/lenovo/TradingAgents')

from tradingagents.dataflows.efinance_source import (
    get_efinance_stock_data,
    get_efinance_fundamentals,
    is_a_share_stock,
    _convert_a_share_code
)
from tradingagents.dataflows.interface import route_to_vendor

print("="*70)
print("           A股数据源诊断工具")
print("="*70)
print()

# 测试1: A股代码检测
print("测试1: A股代码检测")
print("-"*70)
test_codes = [
    '600519.SS',
    '000001.SZ',
    '600036.SS',
    'AAPL',
    'BABA',
    '0700.HK'
]

for code in test_codes:
    result = is_a_share_stock(code)
    status = "[OK] A股" if result else "[NO] 非A股"
    print(f"{code:15} -> {status}")

print()

# 测试2: 代码转换
print("测试2: A股代码转换")
print("-"*70)
test_convert = [
    ('600519.SS', '600519'),
    ('000001.SZ', '000001'),
    ('600036.SS', '600036'),
]

for input_code, expected in test_convert:
    result = _convert_a_share_code(input_code)
    status = "[OK]" if result == expected else "[FAIL]"
    print(f"{status} {input_code} -> {result} (expected: {expected})")

print()

# 测试3: 数据获取（使用efinance）
print("测试3: 使用EFinance获取A股数据")
print("-"*70)

test_stocks = [
    ('000001', '2024-12-01', '2024-12-10'),  # 平安银行
    ('600519', '2024-12-01', '2024-12-10'),  # 贵州茅台
]

for code, start, end in test_stocks:
    print(f"\n获取 {code} 数据（{start} 到 {end}）...")
    result = get_efinance_stock_data(f'{code}.SS', start, end)

    # 检查结果
    if "No data found" in result:
        print(f"  [FAIL] No data found")
    elif "Error fetching" in result:
        print(f"  [FAIL] Error fetching data")
    else:
        # 计算行数
        lines = result.split('\n')
        data_lines = [l for l in lines if l and not l.startswith('#') and not l.startswith('Date')]
        print(f"  [OK] Success! {len(data_lines)} records")
        # 显示前几行
        print(f"\nFirst 5 lines:")
        print('\n'.join(result.split('\n')[:8]))

print()

# 测试4: 使用interface路由（模拟实际调用）
print("测试4: 使用interface路由获取数据")
print("-"*70)

try:
    print("\nTrying to get 000001.SZ data via routing...")
    result = route_to_vendor("get_stock_data", "000001.SZ", "2024-12-01", "2024-12-10")

    if "No data found" in result:
        print("  [FAIL] No data found")
    elif "Error" in result:
        print(f"  [FAIL] Error: {result[:200]}")
    else:
        print("  [OK] Routing success!")
        lines = result.split('\n')
        data_lines = [l for l in lines if l and not l.startswith('#') and not l.startswith('Date')]
        print(f"  Total: {len(data_lines)} records")

except Exception as e:
    print(f"  [FAIL] Exception: {e}")

print()

# 测试5: 基本面数据
print("测试5: 获取基本面数据")
print("-"*70)

try:
    print("\nGetting 000001 fundamentals...")
    result = get_efinance_fundamentals("000001.SZ")
    print("  [OK] Success!")
    print(f"\nFirst 500 chars:\n{result[:500]}")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print()
print("="*70)
print("诊断完成")
print("="*70)
