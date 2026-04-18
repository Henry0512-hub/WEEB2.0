"""
WRDS连接诊断和修复工具
帮助诊断WRDS连接问题并提供解决方案
"""

import sys
import os
import socket
import time
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


def check_network_connectivity():
    """检查网络连接"""
    print("\n[网络诊断]")
    print("-" * 50)

    wrds_host = "wrds-pgdata.wharton.upenn.edu"
    wrds_port = 9737

    print(f"测试连接到 {wrds_host}:{wrds_port}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((wrds_host, wrds_port))
        sock.close()

        if result == 0:
            print("✓ 可以连接到WRDS服务器")
            return True
        else:
            print(f"✗ 无法连接到WRDS服务器 (错误码: {result})")
            return False

    except socket.gaierror:
        print("✗ DNS解析失败 - 请检查网络连接")
        return False
    except socket.timeout:
        print("✗ 连接超时 - 可能需要VPN或校园网")
        return False
    except Exception as e:
        print(f"✗ 网络错误: {str(e)}")
        return False


def check_credentials():
    """检查凭据文件"""
    print("\n[凭据检查]")
    print("-" * 50)

    from tradingagents.utils.credentials import load_wrds_credentials

    creds = load_wrds_credentials()

    if creds:
        print(f"✓ 找到凭据")
        print(f"  用户名: {creds['username']}")
        print(f"  密码: {'*' * len(creds['password'])}")

        # 验证凭据格式
        if len(creds['username']) < 3:
            print("⚠ 警告: 用户名似乎太短")
        if len(creds['password']) < 6:
            print("⚠ 警告: 密码似乎太短")

        return creds
    else:
        print("✗ 未找到凭据")
        print("  请确认 is/wrds.txt 文件存在")
        return None


def check_wrds_package():
    """检查WRDS包"""
    print("\n[包依赖检查]")
    print("-" * 50)

    try:
        import wrds
        print(f"✓ wrds 包已安装 (版本: {wrds.__version__})")
    except ImportError:
        print("✗ wrds 包未安装")
        print("  请运行: pip install wrds")
        return False

    try:
        import psycopg2
        print(f"✓ psycopg2 包已安装")
    except ImportError:
        print("✗ psycopg2 包未安装")
        print("  请运行: pip install psycopg2-binary")
        return False

    return True


def test_connection_with_retry(creds, max_retries=3, delay=5):
    """带重试的连接测试"""
    print("\n[连接测试]")
    print("-" * 50)

    import wrds

    for attempt in range(1, max_retries + 1):
        print(f"尝试 {attempt}/{max_retries}...")

        try:
            # 创建连接
            db = wrds.Connection(
                wrds_username=creds['username'],
                wrds_password=creds['password'],
                autoconnect=False
            )

            # 尝试连接
            db._Connection__make_sa_engine_conn(raise_err=True)

            if db.engine and db.connection:
                print("✓ WRDS连接成功!")
                return db
            else:
                print("✗ 连接对象创建失败")

        except Exception as e:
            error_msg = str(e)

            if "SSL" in error_msg or "Connection reset" in error_msg:
                print(f"✗ SSL连接错误 - 可能需要VPN")
                print(f"  错误: {error_msg[:100]}...")
            elif "authentication" in error_msg.lower():
                print(f"✗ 认证失败 - 请检查用户名和密码")
                print(f"  错误: {error_msg[:100]}...")
            else:
                print(f"✗ 连接失败: {error_msg[:100]}...")

        if attempt < max_retries:
            print(f"等待 {delay} 秒后重试...")
            time.sleep(delay)

    return None


def show_solutions():
    """显示解决方案"""
    print("\n" + "=" * 50)
    print("[常见问题解决方案]")
    print("=" * 50)

    solutions = [
        ("连接被重置 (Connection reset)",
         ["• 确保使用校园网或VPN连接",
          "• 某些地区可能需要特殊网络配置",
          "• 尝试使用移动热点测试"]),

        ("认证失败 (Authentication failed)",
         ["• 检查 is/wrds.txt 中的用户名和密码",
          "• 确认WRDS账户已激活",
          "• 访问 https://wrds.wharton.upenn.edu 重置密码"]),

        ("DNS解析失败",
         ["• 检查网络连接",
          "• 尝试更换DNS服务器为 8.8.8.8",
          "• 使用VPN或校园网"]),

        ("包依赖问题",
         ["• 运行: pip install wrds psycopg2-binary",
          "• 或: pip install -r requirements.txt"])
    ]

    for problem, solutions_list in solutions:
        print(f"\n{problem}:")
        for solution in solutions_list:
            print(f"  {solution}")


def run_diagnostic():
    """运行完整诊断"""
    print("=" * 50)
    print("WRDS 连接诊断工具")
    print("=" * 50)

    # 检查包依赖
    if not check_wrds_package():
        return False

    # 检查凭据
    creds = check_credentials()
    if not creds:
        return False

    # 检查网络
    network_ok = check_network_connectivity()

    if not network_ok:
        print("\n⚠ 网络连接存在问题，WRDS可能需要VPN或校园网访问")

    # 尝试连接
    db = test_connection_with_retry(creds)

    if db:
        print("\n✓ 诊断完成 - 一切正常!")
        db.close()
        return True
    else:
        print("\n✗ 连接失败")
        show_solutions()
        return False


def interactive_fix():
    """交互式修复"""
    print("\n" + "=" * 50)
    print("[WRDS配置修复]")
    print("=" * 50)

    print("\n选择操作:")
    print("  1. 重新输入WRDS凭据")
    print("  2. 测试现有凭据")
    print("  3. 显示凭据文件路径")
    print("  0. 返回")

    choice = input("\n请选择 (0-3): ").strip()

    if choice == "1":
        username = input("请输入WRDS用户名: ").strip()
        password = input("请输入WRDS密码: ").strip()

        if username and password:
            # 写入文件
            wrds_file = project_root / "is" / "wrds.txt"
            wrds_file.parent.mkdir(parents=True, exist_ok=True)

            with open(wrds_file, 'w', encoding='utf-8') as f:
                f.write(f"username: {username}\n")
                f.write(f"password: {password}\n")

            print(f"✓ 凭据已保存到 {wrds_file}")
            print("  请重新运行测试")

    elif choice == "2":
        creds = check_credentials()
        if creds:
            test_connection_with_retry(creds)

    elif choice == "3":
        wrds_file = project_root / "is" / "wrds.txt"
        print(f"\n凭据文件路径: {wrds_file}")
        print(f"文件是否存在: {'是' if wrds_file.exists() else '否'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WRDS连接诊断工具')
    parser.add_argument('--fix', action='store_true', help='进入交互式修复模式')
    parser.add_argument('--quick', action='store_true', help='快速测试')

    args = parser.parse_args()

    if args.fix:
        # 先运行诊断
        run_diagnostic()
        # 然后进入修复模式
        interactive_fix()
    elif args.quick:
        # 快速测试
        creds = check_credentials()
        if creds:
            test_connection_with_retry(creds, max_retries=1)
    else:
        # 完整诊断
        run_diagnostic()

        # 询问是否需要修复
        if input("\n是否需要修复配置? (y/n): ").strip().lower() == 'y':
            interactive_fix()
