"""
测试WRDS优先级功能
验证2024-12-31之前的美股数据优先使用WRDS
"""

from intelligent_data_fetcher import IntelligentDataFetcher
from datetime import datetime

def test_wrds_priority():
    """测试WRDS优先级"""
    print("="*70)
    print("WRDS优先级测试")
    print("="*70)
    print()
    print("测试策略：")
    print("- 2024-12-31之前的美股 → 应优先使用WRDS")
    print("- 2024-12-31之后的美股 → 使用Alpha Vantage等实时数据源")
    print("- 中概股 → 使用akshares")
    print("- A股 → 使用EFinance（未来集成）")
    print()

    # 测试用例
    test_cases = [
        {
            "name": "美股历史数据（应使用WRDS）",
            "ticker": "AAPL",
            "start_date": "2024-06-15",
            "end_date": "2024-08-15",
            "expected_priority": "WRDS"
        },
        {
            "name": "美股实时数据（不使用WRDS）",
            "ticker": "TSLA",
            "start_date": "2025-01-15",
            "end_date": "2025-03-20",
            "expected_priority": "Alpha Vantage"
        },
        {
            "name": "中概股（不使用WRDS）",
            "ticker": "BABA",
            "start_date": "2024-06-01",
            "end_date": "2024-08-01",
            "expected_priority": "akshares"
        },
        {
            "name": "美股近期数据（不使用WRDS）",
            "ticker": "NVDA",
            "start_date": "2025-03-01",
            "end_date": "2025-04-09",
            "expected_priority": "Alpha Vantage"
        }
    ]

    print("="*70)
    print("开始测试...")
    print("="*70)
    print()

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"股票: {test_case['ticker']}")
        print(f"日期: {test_case['start_date']} 到 {test_case['end_date']}")
        print(f"预期优先级: {test_case['expected_priority']}")
        print()

        # 创建数据获取器
        fetcher = IntelligentDataFetcher(
            test_case['ticker'],
            test_case['start_date'],
            test_case['end_date']
        )

        # 检查WRDS优先级判断
        should_use_wrds = fetcher._should_use_wrds()
        is_us_stock = fetcher._is_us_stock()

        print(f"[判断结果]")
        print(f"  - 是否应使用WRDS: {should_use_wrds}")
        print(f"  - 是否是美股: {is_us_stock}")
        print()

        # 尝试获取数据
        try:
            print(f"[开始获取数据...]")
            data, source = fetcher.fetch_stock_data()

            print()
            print(f"[成功] ✓")
            print(f"  - 实际数据源: {source}")
            print(f"  - 数据量: {len(data)} 条")
            print(f"  - 价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")

            # 验证优先级
            if test_case['expected_priority'] == "WRDS":
                if should_use_wrds:
                    status = "✓ 优先级正确"
                else:
                    status = "✗ 优先级错误（应该使用WRDS）"
            else:
                if not should_use_wrds:
                    status = "✓ 优先级正确"
                else:
                    status = "✗ 优先级错误（不应该使用WRDS）"

            print(f"  - 验证结果: {status}")

            results.append({
                "name": test_case['name'],
                "ticker": test_case['ticker'],
                "expected": test_case['expected_priority'],
                "actual": source,
                "should_use_wrds": should_use_wrds,
                "status": "通过" if ("正确" in status) else "失败"
            })

        except Exception as e:
            print(f"[失败] ✗")
            print(f"  - 错误信息: {e}")

            results.append({
                "name": test_case['name'],
                "ticker": test_case['ticker'],
                "expected": test_case['expected_priority'],
                "actual": "获取失败",
                "should_use_wrds": should_use_wrds,
                "status": "失败"
            })

    # 打印总结
    print()
    print("="*70)
    print("测试总结")
    print("="*70)
    print()

    print(f"{'测试名称':<30} {'股票':<10} {'预期':<15} {'实际':<15} {'状态':<10}")
    print("-"*70)

    passed = 0
    failed = 0

    for result in results:
        print(f"{result['name']:<30} {result['ticker']:<10} {result['expected']:<15} {result['actual']:<15} {result['status']:<10}")
        if result['status'] == "通过":
            passed += 1
        else:
            failed += 1

    print("-"*70)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print()

    if failed == 0:
        print("✓ 所有测试通过！WRDS优先级功能正常。")
    else:
        print(f"✗ 有 {failed} 个测试失败，请检查。")

    print()
    print("="*70)

if __name__ == "__main__":
    test_wrds_priority()
