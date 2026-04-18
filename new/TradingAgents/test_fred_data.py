"""
使用 FRED API 获取实际经济数据
"""
from fredapi import Fred
import pandas as pd
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量或直接设置
api_key = os.getenv("FRED_API_KEY", "your-fred-api-key-here")

print("=== 获取 FRED 经济数据 ===\n")

if api_key == "your-fred-api-key-here":
    print("[错误] 请先设置 FRED API Key")
    print("\n1. 访问 https://fred.stlouisfed.org/docs/api/api_key.html")
    print("2. 注册免费的 API Key")
    print("3. 在 .env 文件中添加: FRED_API_KEY=your-key")
    exit(1)

try:
    fred = Fred(api_key=api_key)

    print("正在获取经济数据...\n")

    # 定义要获取的经济指标
    indicators = {
        'GDP': '国内生产总值',
        'CPIAUCSL': '消费者物价指数',
        'UNRATE': '失业率',
        'FEDFUNDS': '联邦基金利率',
        'GS10': '10年期国债收益率',
        'SP500': '标普 500 指数',
        'DEXUSEU': '美元欧元汇率',
        'PAYEMS': '非农就业人数'
    }

    results = {}

    for code, name in indicators.items():
        try:
            # 获取最近的数据
            data = fred.get_series(code, observation_start='2023-01-01')

            if len(data) > 0:
                latest_value = data.iloc[-1]
                latest_date = data.index[-1]

                results[code] = {
                    'name': name,
                    'value': latest_value,
                    'date': latest_date,
                    'series': data
                }

                print(f"[OK] {name} ({code})")
                print(f"     最新值: {latest_value}")
                print(f"     日期: {latest_date.strftime('%Y-%m-%d')}")
                print()
        except Exception as e:
            print(f"[ERROR] 获取 {name} 失败: {e}\n")

    # 生成经济分析报告
    print("="*60)
    print("   经济数据摘要")
    print("="*60)

    if 'UNRATE' in results and 'FEDFUNDS' in results:
        unemployment = results['UNRATE']['value']
        fed_rate = results['FEDFUNDS']['value']

        print(f"\n失业率: {unemployment:.2f}%")
        print(f"联邦基金利率: {fed_rate:.2f}%")

        if unemployment < 4:
            print("=> 劳动力市场紧张")
        elif unemployment > 6:
            print("=> 劳动力市场疲软")

        if fed_rate > 3:
            print("=> 紧缩货币政策")
        elif fed_rate < 2:
            print("=> 宽松货币政策")

    if 'CPIAUCSL' in results:
        cpi = results['CPIAUCSL']['value']
        print(f"\nCPI 指数: {cpi:.2f}")

    if 'GDP' in results:
        gdp = results['GDP']['value']
        print(f"GDP: {gdp:.2f} 十亿美元")

    print("\n" + "="*60)
    print("[OK] 数据获取完成！")

    # 保存到 CSV
    print("\n正在保存数据到 CSV 文件...")
    for code, data in results.items():
        filename = f"fred_{code.lower()}.csv"
        data['series'].to_csv(filename)
        print(f"  已保存: {filename}")

    print("\n[完成] 所有数据已保存")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n可能的问题：")
    print("1. API Key 无效")
    print("2. 网络连接失败")
    print("3. 超出 API 限制")

print("\n=== 完成 ===")
