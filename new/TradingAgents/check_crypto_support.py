# -*- coding: utf-8 -*-
"""
检查加密货币代码是否被支持
"""
import sys
sys.path.append('C:\\Users\\lenovo\\TradingAgents')

from tradingagents.dataflows.coingecko_source import (
    get_coingecko_id,
    is_cryptocurrency
)

print("="*70)
print("加密货币代码检查工具")
print("="*70)
print()

while True:
    try:
        user_input = input("请输入加密货币代码（输入 'q' 退出）: ").strip()

        if user_input.lower() == 'q':
            print("退出程序")
            break

        if not user_input:
            continue

        ticker = user_input.upper()

        # 检查1: 本地支持列表
        is_supported = is_cryptocurrency(ticker)
        print()
        print(f"检查币种: {ticker}")
        print("-"*70)

        if is_supported:
            print(f"[支持] {ticker} 在本地支持列表中")

            # 检查2: CoinGecko ID映射
            coin_id = get_coingecko_id(ticker)
            print(f"[ID映射] {ticker} -> {coin_id}")
            print()
            print("[建议] 该币种应该可以正常使用")
        else:
            print(f"[不支持] {ticker} 不在本地支持列表中")
            print()
            print("[建议] 该币种可能无法获取数据")
            print()
            print("支持的币种列表:")
            print("主流: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT")
            print("DeFi: UNI, AAVE, LINK, COMP")
            print("公链: MATIC, AVAX, ATOM, LTC, ETC")
            print("其他: OP, ARB, INJ, FET, RNDR")

        print()
        print("="*70)
        print()

    except KeyboardInterrupt:
        print()
        print("退出程序")
        break
    except Exception as e:
        print(f"[错误] {e}")
        print()

print()
print("提示: 使用支持列表中的币种代码（大写）")
