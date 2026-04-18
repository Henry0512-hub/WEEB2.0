# -*- coding: utf-8 -*-
import sys
import requests

print("="*70)
print("网络连接测试")
print("="*70)
print()

# 测试1: CoinGecko API
print("[测试1] CoinGecko API连接...")
try:
    url = "https://api.coingecko.com/api/v3/ping"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print("[成功] CoinGecko API可以访问!")
    else:
        print(f"[失败] HTTP状态码: {response.status_code}")
except Exception as e:
    print(f"[失败] {e}")

print()

# 测试2: 获取比特币价格
print("[测试2] 获取比特币价格...")
try:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        btc_price = data['bitcoin']['usd']
        btc_change = data['bitcoin']['usd_24h_change']
        print(f"[成功] BTC价格: ${btc_price:,.2f}")
        print(f"[成功] BTC 24h变化: {btc_change:.2f}%")
    else:
        print(f"[失败] HTTP状态码: {response.status_code}")
except Exception as e:
    print(f"[失败] {e}")

print()

# 测试3: 获取以太坊价格
print("[测试3] 获取以太坊价格...")
try:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "ethereum",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        eth_price = data['ethereum']['usd']
        eth_change = data['ethereum']['usd_24h_change']
        print(f"[成功] ETH价格: ${eth_price:,.2f}")
        print(f"[成功] ETH 24h变化: {eth_change:.2f}%")
    else:
        print(f"[失败] HTTP状态码: {response.status_code}")
except Exception as e:
    print(f"[失败] {e}")

print()
print("="*70)
print("测试完成!")
print("="*70)
