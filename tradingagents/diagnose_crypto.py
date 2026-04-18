# -*- coding: utf-8 -*-
"""
加密货币数据诊断工具
检查CoinGecko API支持哪些币种
"""
import sys
sys.path.append('C:\\Users\\lenovo\\TradingAgents')

from tradingagents.dataflows.coingecko_source import (
    get_coingecko_id,
    is_cryptocurrency
)
import requests

print("="*70)
print("加密货币数据诊断工具")
print("="*70)
print()

# 测试币种列表
test_coins = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
    "MATIC", "AVAX", "LINK", "UNI", "ATOM", "LTC", "ETC"
]

print("[测试1] 检查本地币种识别:")
print("-"*70)
for coin in test_coins:
    is_supported = is_cryptocurrency(coin)
    status = "[支持]" if is_supported else "[不支持]"
    print(f"{status} {coin}")

print()
print("[测试2] 检查CoinGecko ID映射:")
print("-"*70)
for coin in test_coins:
    coin_id = get_coingecko_id(coin)
    print(f"{coin:10s} -> {coin_id}")

print()
print("[测试3] 测试CoinGecko API数据获取:")
print("-"*70)

# 测试几个主流币种的实际数据获取
priority_coins = ["BTC", "ETH", "BNB"]

for coin in priority_coins:
    try:
        coin_id = get_coingecko_id(coin)

        # 测试获取价格数据
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price = data[coin_id]['usd']
                change = data[coin_id]['usd_24h_change']
                print(f"[成功] {coin}: ${price:,.2f} (24h: {change:.2f}%)")
            else:
                print(f"[失败] {coin}: API返回数据为空")
        else:
            print(f"[失败] {coin}: HTTP {response.status_code}")

    except Exception as e:
        print(f"[错误] {coin}: {e}")

print()
print("[测试4] 检查CoinGecko完整列表:")
print("-"*70)
print("正在获取CoinGecko支持的币种列表...")

try:
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        coins_list = response.json()
        print(f"[成功] CoinGecko共支持 {len(coins_list):,} 个币种")
        print()

        # 检查我们的测试币种是否在列表中
        print("检查常用币种:")
        for coin in priority_coins:
            coin_id = get_coingecko_id(coin)
            found = any(c['id'] == coin_id for c in coins_list)
            status = "[存在]" if found else "[不存在]"
            print(f"{status} {coin} ({coin_id})")

    else:
        print(f"[失败] HTTP {response.status_code}")

except Exception as e:
    print(f"[错误] {e}")

print()
print("="*70)
print("诊断完成")
print("="*70)
print()
print("建议:")
print("1. 如果币种在本地支持列表但CoinGecko返回404")
print("2. 可能是CoinGecko ID映射不正确")
print("3. 或者该币种在CoinGecko上暂未支持")
print()
print("请尝试使用以下币种:")
print("  BTC (比特币), ETH (以太坊), BNB (币安币)")
print()
