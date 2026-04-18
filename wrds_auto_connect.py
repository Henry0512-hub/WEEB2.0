"""
WRDS自动连接脚本
自动从 is/wrds.txt 读取账号密码，建立WRDS连接并进行测试
"""

import sys
import os
from pathlib import Path

# 设置Windows控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.credentials import load_wrds_credentials
from tradingagents.dataflows.wrds_source import (
    get_wrds_connection,
    get_stock_data_wrds,
    get_fundamentals_wrds,
)


def test_wrds_connection():
    """测试WRDS连接"""
    print("=" * 60)
    print("WRDS 自动连接测试")
    print("=" * 60)

    # 加载凭据
    print("\n[1] 加载WRDS凭据...")
    creds = load_wrds_credentials()

    if not creds:
        print("❌ 错误: 无法找到WRDS凭据")
        print("   请确认 is/wrds.txt 文件存在并包含正确的账号密码")
        return False

    username = creds["username"]
    print(f"✓ 用户名: {username}")

    # 测试连接
    print("\n[2] 建立WRDS连接...")
    try:
        db = get_wrds_connection()
        print("✓ WRDS连接成功!")
    except Exception as e:
        print(f"❌ WRDS连接失败: {str(e)}")
        return False

    # 测试查询
    print("\n[3] 测试数据查询...")
    test_symbol = "AAPL"

    try:
        print(f"   获取 {test_symbol} 的股票数据...")
        stock_data = get_stock_data_wrds(
            symbol=test_symbol,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        if stock_data.startswith("Error"):
            print(f"❌ 获取股票数据失败")
            return False

        print("✓ 股票数据获取成功!")

        # 显示前几行数据
        lines = stock_data.split('\n')
        print("\n   数据预览:")
        for line in lines[:8]:
            if line.strip():
                print(f"   {line}")

    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return False

    # 测试基本面数据
    print(f"\n   获取 {test_symbol} 的基本面数据...")
    try:
        fundamentals = get_fundamentals_wrds(test_symbol)

        if fundamentals.startswith("Error"):
            print(f"❌ 获取基本面数据失败")
            return False

        print("✓ 基本面数据获取成功!")

    except Exception as e:
        print(f"❌ 基本面查询失败: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("✓ 所有测试通过! WRDS连接正常")
    print("=" * 60)

    return True


def interactive_query():
    """交互式查询模式"""
    print("\n" + "=" * 60)
    print("WRDS 交互式查询模式")
    print("=" * 60)

    # 获取连接
    try:
        db = get_wrds_connection()
        print("✓ WRDS已连接\n")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return

    while True:
        print("\n请选择查询类型:")
        print("  1. 股票价格数据")
        print("  2. 基本面数据")
        print("  3. 资产负债表")
        print("  4. 利润表")
        print("  5. 现金流量表")
        print("  0. 退出")

        choice = input("\n请输入选项 (0-5): ").strip()

        if choice == "0":
            print("退出交互模式")
            break

        symbol = input("请输入股票代码 (如 AAPL): ").strip().upper()

        if not symbol:
            print("❌ 股票代码不能为空")
            continue

        try:
            if choice == "1":
                start_date = input("开始日期 (yyyy-mm-dd, 默认: 2024-01-01): ").strip() or "2024-01-01"
                end_date = input("结束日期 (yyyy-mm-dd, 默认: 2024-12-31): ").strip() or "2024-12-31"

                print(f"\n正在获取 {symbol} 的股票数据...")
                data = get_stock_data_wrds(symbol, start_date, end_date)

            elif choice == "2":
                print(f"\n正在获取 {symbol} 的基本面数据...")
                data = get_fundamentals_wrds(symbol)

            elif choice == "3":
                from tradingagents.dataflows.wrds_source import get_balance_sheet_wrds
                print(f"\n正在获取 {symbol} 的资产负债表...")
                data = get_balance_sheet_wrds(symbol)

            elif choice == "4":
                from tradingagents.dataflows.wrds_source import get_income_statement_wrds
                print(f"\n正在获取 {symbol} 的利润表...")
                data = get_income_statement_wrds(symbol)

            elif choice == "5":
                from tradingagents.dataflows.wrds_source import get_cashflow_wrds
                print(f"\n正在获取 {symbol} 的现金流量表...")
                data = get_cashflow_wrds(symbol)

            else:
                print("❌ 无效选项")
                continue

            if data.startswith("Error"):
                print(f"❌ 查询失败: {data}")
            else:
                lines = data.split('\n')
                print("\n数据预览 (前15行):")
                for line in lines[:15]:
                    print(line)

                # 询问是否保存
                save = input("\n是否保存到文件? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("请输入文件名 (默认: wrds_output.csv): ").strip() or "wrds_output.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(data)
                    print(f"✓ 数据已保存到 {filename}")

        except Exception as e:
            print(f"❌ 查询出错: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WRDS自动连接工具')
    parser.add_argument('--test', action='store_true', help='运行连接测试')
    parser.add_argument('--interactive', '-i', action='store_true', help='进入交互式查询模式')

    args = parser.parse_args()

    if args.test or not args.interactive:
        # 默认运行测试
        success = test_wrds_connection()

        if success and args.interactive == False:
            # 测试成功后询问是否进入交互模式
            answer = input("\n是否进入交互式查询模式? (y/n): ").strip().lower()
            if answer == 'y':
                interactive_query()

    if args.interactive:
        interactive_query()
