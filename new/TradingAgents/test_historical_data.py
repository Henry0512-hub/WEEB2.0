# -*- coding: utf-8 -*-
"""
测试CoinGecko历史数据获取
找出导致404错误的原因
"""
import requests
from datetime import datetime, timedelta

print("="*70)
print("CoinGecko历史数据测试")
print("="*70)
print()

# 计算日期范围（最近7天）
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

start_timestamp = int(start_date.timestamp())
end_timestamp = int(end_date.timestamp()) + 86400

print(f"测试日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
print()

# 测试币种
test_coins = [
    ("BTC", "bitcoin"),
    ("ETH", "ethereum"),
    ("BNB", "binancecoin"),
]

for symbol, coin_id in test_coins:
    print(f"[测试] {symbol} ({coin_id})...")

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        "vs_currency": "usd",
        "from": start_timestamp,
        "to": end_timestamp
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            prices = data.get("prices", [])
            print(f"  [成功] 获取到 {len(prices)} 个价格数据点")

            if len(prices) > 0:
                # 显示最新价格
                latest_price = prices[-1][1]
                print(f"  最新价格: ${latest_price:,.2f}")
        else:
            print(f"  [失败] HTTP {response.status_code}")
            print(f"  响应: {response.text[:200]}")

    except Exception as e:
        print(f"  [错误] {e}")

    print()

print("="*70)
print("测试完成")
print("="*70)
print()
print("如果所有测试都成功，问题可能在:")
print("1. 交易系统中使用了不支持的币种")
print("2. API调用频率限制（需要等待）")
print("3. 数据格式解析问题")
