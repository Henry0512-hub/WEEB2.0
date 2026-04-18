"""
WRDS连接测试脚本 - 验证自动连接是否工作
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

# 添加项目路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.credentials import load_wrds_credentials
from tradingagents.dataflows.wrds_source import get_wrds_connection


def test_credentials():
    """测试凭据加载"""
    print("=" * 60)
    print("WRDS凭据测试")
    print("=" * 60)

    creds = load_wrds_credentials()

    if creds:
        print(f"✓ 凭据加载成功")
        print(f"  用户名: {creds['username']}")
        print(f"  密码长度: {len(creds['password'])} 字符")
        return creds
    else:
        print("✗ 凭据加载失败")
        return None


def test_connection(creds):
    """测试WRDS连接"""
    print("\n" + "=" * 60)
    print("WRDS连接测试")
    print("=" * 60)

    if not creds:
        print("✗ 跳过：没有凭据")
        return False

    try:
        print("正在连接WRDS...")
        db = get_wrds_connection()
        print("✓ WRDS连接成功!")

        # 测试简单查询
        print("\n测试简单查询...")
        import pandas as pd
        result = db.raw_sql("SELECT current_database(), current_user")
        print(f"✓ 查询成功!")
        print(f"  数据库: {result.iloc[0, 0]}")
        print(f"  用户: {result.iloc[0, 1]}")

        return True

    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 测试凭据
    creds = test_credentials()

    # 测试连接
    success = test_connection(creds)

    print("\n" + "=" * 60)
    if success:
        print("✓ 所有测试通过!")
    else:
        print("✗ 测试失败 - 请检查网络连接和凭据")
    print("=" * 60)
