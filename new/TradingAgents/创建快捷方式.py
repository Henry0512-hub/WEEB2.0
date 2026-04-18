"""
创建 TradingAgents 桌面快捷方式
"""
import os
import sys
from pathlib import Path
import shutil

def create_shortcut():
    """创建桌面快捷方式"""

    # 获取桌面路径
    desktop = Path.home() / "Desktop"

    # 获取 TradingAgents 目录
    if len(sys.argv) > 1:
        tradingagents_dir = Path(sys.argv[1])
    else:
        # 默认目录
        tradingagents_dir = Path.cwd()

        # 如果当前目录不是 TradingAgents，尝试找到它
        if not (tradingagents_dir / "一键启动.bat").exists():
            tradingagents_dir = Path("C:/Users/lenovo/TradingAgents")

    print("=" * 70)
    print("   TradingAgents - 创建桌面快捷方式")
    print("=" * 70)
    print()

    # 检查目录
    if not tradingagents_dir.exists():
        print(f"[错误] 找不到 TradingAgents 目录: {tradingagents_dir}")
        print()
        input("按 Enter 键退出...")
        return

    print(f"[OK] TradingAgents 目录: {tradingagents_dir}")

    # 方案 1: 复制启动脚本到桌面
    launcher_bat = tradingagents_dir / "一键启动.bat"

    if launcher_bat.exists():
        # 创建一个简化的启动脚本到桌面
        desktop_launcher = desktop / "启动TradingAgents.bat"

        with open(desktop_launcher, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write(f'cd /d "{tradingagents_dir}"\n')
            f.write('call 一键启动.bat\n')

        print(f"[OK] 已创建: {desktop_launcher}")

    # 方案 2: 创建 Python 启动脚本到桌面
    desktop_py = desktop / "启动TradingAgents.py"

    with open(desktop_py, 'w', encoding='utf-8') as f:
        f.write('import subprocess\n')
        f.write('import os\n')
        f.write(f'os.chdir(r"{tradingagents_dir}")\n')
        f.write('subprocess.call(["python", "一键启动.py"])\n')

    print(f"[OK] 已创建: {desktop_py}")

    print()
    print("=" * 70)
    print("   创建完成！")
    print("=" * 70)
    print()
    print("桌面上现在有两个启动文件：")
    print()
    print("1. 启动TradingAgents.bat - 双击运行（推荐）")
    print("2. 启动TradingAgents.py - Python 脚本")
    print()
    print("双击任一文件即可启动 TradingAgents！")
    print()

if __name__ == "__main__":
    create_shortcut()
