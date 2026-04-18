"""
测试 FRED API（美联储经济数据库）

FRED (Federal Reserve Economic Data) 提供免费的美国宏观经济数据
包括：GDP、CPI、失业率、利率等

注册地址：https://fred.stlouisfed.org/docs/api/api_key.html
"""

from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta

# 注意：需要 FRED API Key
# 如果没有，可以注册获取免费的 API Key
api_key = "your-fred-api-key-here"  # 替换为你的 FRED API Key

print("=== FRED API 测试 ===\n")

if api_key == "your-fred-api-key-here":
    print("[提示] 需要设置 FRED API Key")
    print("\n获取步骤：")
    print("1. 访问：https://fred.stlouisfed.org/docs/api/api_key.html")
    print("2. 点击 'Request API Key'")
    print("3. 填写表单（免费）")
    print("4. 复制 API Key 到本文件")
    print("\n继续演示部分无需 API Key 的功能...\n")

    # 演示一些常用的经济指标代码
    print("=== 常用 FRED 经济指标 ===")
    print("\nGDP（国内生产总值）:")
    print("  代码: GDP")
    print("  说明: 美国季度 GDP")

    print("\nCPI（消费者物价指数）:")
    print("  代码: CPIAUCSL")
    print("  说明: 城市消费者物价指数")

    print("\n失业率:")
    print("  代码: UNRATE")
    print("  说明: 美国失业率")

    print("\n联邦基金利率:")
    print("  代码: FEDFUNDS")
    print("  说明: 美国基准利率")

    print("\n10年期国债收益率:")
    print("  代码: GS10")
    print("  说明: 10 年期美国国债收益率")

    print("\n标普 500 指数:")
    print("  代码: SP500")
    print("  说明: 标准普尔 500 指数")

    print("\n\n=== 在 TradingAgents 中的使用 ===")
    print("FRED 数据可以用于：")
    print("1. 宏观经济分析")
    print("2. 利率环境评估")
    print("3. 通胀趋势分析")
    print("4. 经济周期判断")

    print("\n\n获取 API Key 后，可以运行：")
    print("  python test_fred_data.py")

else:
    try:
        # 创建 FRED 实例
        fred = Fred(api_key=api_key)

        print("连接 FRED API...\n")

        # 获取 GDP 数据
        print("1. 获取美国 GDP 数据...")
        gdp = fred.get_series('GDP')
        print(f"   最新 GDP: {gdp.iloc[-1]:.2f} 十亿美元")
        print(f"   数据期数: {len(gdp)}")

        # 获取 CPI 数据
        print("\n2. 获取 CPI 数据...")
        cpi = fred.get_series('CPIAUCSL')
        print(f"   最新 CPI: {cpi.iloc[-1]:.2f}")

        # 获取失业率
        print("\n3. 获取失业率...")
        unemployment = fred.get_series('UNRATE')
        print(f"   最新失业率: {unemployment.iloc[-1]:.2f}%")

        # 获取联邦基金利率
        print("\n4. 获取联邦基金利率...")
        fed_funds = fred.get_series('FEDFUNDS')
        print(f"   最新利率: {fed_funds.iloc[-1]:.2f}%")

        print("\n[OK] FRED API 连接成功！")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\n可能的原因：")
        print("1. API Key 无效")
        print("2. 网络连接问题")
        print("3. 超出请求限制")

print("\n=== 测试完成 ===")

# 使用示例
print("\n\n=== 代码示例 ===")
print("""
from fredapi import Fred

# 创建 FRED 实例
fred = Fred(api_key='your-api-key')

# 获取 GDP 数据
gdp = fred.get_series('GDP', observation_start='2020-01-01')
print(gdp.tail())

# 获取多个指标
indicators = ['GDP', 'CPIAUCSL', 'UNRATE', 'FEDFUNDS']
for indicator in indicators:
    data = fred.get_series(indicator)
    print(f"{indicator}: {data.iloc[-1]}")
""")
