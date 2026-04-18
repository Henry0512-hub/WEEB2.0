"""
创建.pgpass文件以避免WRDS交互式输入
"""

import os
from pathlib import Path
from tradingagents.utils.credentials import load_wrds_credentials

def create_pgpass():
    """创建PostgreSQL .pgpass文件"""
    creds = load_wrds_credentials()
    if not creds:
        print("错误: 无法加载WRDS凭据")
        return False

    username = creds["username"]
    password = creds["password"]

    # .pgpass文件格式: hostname:port:database:username:password
    pgpass_content = f"wrds-pgdata.wharton.upenn.edu:9737:wrds:{username}:{password}\n"

    # 确定用户主目录
    home = Path.home()

    # 创建.pgpass文件
    pgpass_file = home / ".pgpass"

    try:
        with open(pgpass_file, 'w') as f:
            f.write(pgpass_content)

        # 设置文件权限为仅用户可读写 (Windows上可能不支持)
        try:
            os.chmod(pgpass_file, 0o600)
        except:
            pass  # Windows可能不支持

        print(f"✓ 已创建 .pgpass 文件: {pgpass_file}")
        print(f"  用户名: {username}")
        return True

    except Exception as e:
        print(f"✗ 创建 .pgpass 文件失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("创建WRDS .pgpass配置文件")
    print("=" * 60)

    if create_pgpass():
        print("\n✓ 配置完成! 现在可以自动连接WRDS")
        print("\n测试连接:")
        print("  python test_wrds_simple.py")
    else:
        print("\n✗ 配置失败")
