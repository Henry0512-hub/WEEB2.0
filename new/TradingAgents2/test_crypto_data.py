"""
测试加密货币数据获取

测试CoinGecko API是否正常工作
"""

import sys
sys.path.append('C:\\Users\\lenovo\\TradingAgents')

from tradingagents.dataflows.coingecko_source import (
    get_coingecko_price_data,
    get_coingecko_market_info,
    is_cryptocurrency,
    get_coingecko_id
)
from datetime import datetime, timedelta


def test_crypto_detection():
    """测试加密货币检测功能"""
    print("="*70)
    print("测试 1: 加密货币代码识别")
    print("="*70)
    print()

    test_symbols = ["BTC", "ETH", "AAPL", "SOL", "TSLA"]

    for symbol in test_symbols:
        result = is_cryptocurrency(symbol)
        status = "✓ 加密货币" if result else "✗ 非加密货币"
        print(f"{symbol:10s} - {status}")

    print()


def test_coingecko_id_mapping():
    """测试CoinGecko ID映射"""
    print("="*70)
    print("测试 2: CoinGecko ID 映射")
    print("="*70)
    print()

    test_symbols = ["BTC", "ETH", "SOL", "DOGE", "UNKNOWN"]

    for symbol in test_symbols:
        coin_id = get_coingecko_id(symbol)
        print(f"{symbol:10s} -> {coin_id}")

    print()


def test_price_data():
    """测试价格数据获取"""
    print("="*70)
    print("测试 3: 加密货币价格数据获取")
    print("="*70)
    print()

    # 计算日期范围（最近7天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"获取 BTC 价格数据（{start_str} 到 {end_str}）...")
    print()

    try:
        data = get_coingecko_price_data("BTC", start_str, end_str)
        print(data[:500])  # 只打印前500个字符
        print("... (数据已截断)")
        print()
        print("✓ 价格数据获取成功！")
    except Exception as e:
        print(f"✗ 价格数据获取失败: {e}")

    print()


def test_market_info():
    """测试市场信息获取"""
    print("="*70)
    print("测试 4: 加密货币市场信息")
    print("="*70)
    print()

    test_coins = ["BTC", "ETH"]

    for coin in test_coins:
        print(f"获取 {coin} 市场信息...")
        print()
        try:
            info = get_coingecko_market_info(coin)
            print(info)
            print()
            print("✓ 市场信息获取成功！")
        except Exception as e:
            print(f"✗ 市场信息获取失败: {e}")
        print()
        print("-" * 70)
        print()


def main():
    print()
    print("="*70)
    print("       TradingAgents - 加密货币数据测试")
    print("="*70)
    print()

    try:
        # 运行所有测试
        test_crypto_detection()
        input("按 Enter 键继续到下一个测试...")

        test_coingecko_id_mapping()
        input("按 Enter 键继续到下一个测试...")

        test_price_data()
        input("按 Enter 键继续到下一个测试...")

        test_market_info()

        print()
        print("="*70)
        print("✓ 所有测试完成！")
        print("="*70)
        print()

    except Exception as e:
        print()
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    input("按 Enter 键退出...")


if __name__ == "__main__":
    main()
