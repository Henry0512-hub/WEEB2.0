"""
简单测试CoinGecko API
"""

import requests
from datetime import datetime, timedelta


def test_coingecko_api():
    """测试CoinGecko API连接"""
    print("测试 CoinGecko API 连接...")
    print()

    # 测试获取比特币价格
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        print("✓ API连接成功！")
        print()
        print("当前价格：")
        print(f"BTC: ${data['bitcoin']['usd']:,.2f}")
        print(f"  24h变化: {data['bitcoin']['usd_24h_change']:.2f}%")
        print(f"  市值: ${data['bitcoin']['usd_market_cap']:,.0f}")
        print()
        print(f"ETH: ${data['ethereum']['usd']:,.2f}")
        print(f"  24h变化: {data['ethereum']['usd_24h_change']:.2f}%")
        print(f"  市值: ${data['ethereum']['usd_market_cap']:,.0f}")
        print()
        return True

    except Exception as e:
        print(f"✗ API连接失败: {e}")
        return False


def test_historical_data():
    """测试历史数据获取"""
    print("测试历史数据获取...")
    print()

    coin_id = "bitcoin"
    end_timestamp = int(datetime.now().timestamp())
    start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        "vs_currency": "usd",
        "from": start_timestamp,
        "to": end_timestamp
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        prices = data.get("prices", [])
        print(f"✓ 成功获取 {len(prices)} 个价格数据点")
        print()
        print("最近5个数据点：")
        for i in range(min(5, len(prices))):
            timestamp = prices[-5+i][0] / 1000
            date = datetime.fromtimestamp(timestamp)
            price = prices[-5+i][1]
            print(f"  {date.strftime('%Y-%m-%d %H:%M')}: ${price:,.2f}")
        print()
        return True

    except Exception as e:
        print(f"✗ 历史数据获取失败: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("       CoinGecko API 测试")
    print("="*70)
    print()

    # 测试基本连接
    if test_coingecko_api():
        print("-" * 70)
        print()

    # 测试历史数据
    if test_historical_data():
        print("-" * 70)
        print()

    print("="*70)
    print("测试完成！")
    print("="*70)
    print()

    input("按 Enter 键退出...")
