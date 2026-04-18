#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TradingAgents 一键启动脚本
提供交互式菜单选择启动模式
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """打印横幅"""
    print("=" * 70)
    print("           TradingAgents - 一键启动")
    print("=" * 70)
    print()


def check_python():
    """检查 Python 环境"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"[错误] Python 版本过低: {version.major}.{version.minor}")
            print("需要 Python 3.10 或更高版本")
            return False
    except Exception as e:
        print(f"[错误] 无法检查 Python: {e}")
        return False


def check_env():
    """检查环境配置"""
    print("\n配置状态:")

    checks = {
        ".env 文件": os.path.exists(".env"),
        "DeepSeek API": "OPENAI_API_KEY" in os.environ or os.path.exists(".env"),
        "Gemini API": "GOOGLE_API_KEY" in os.environ or os.path.exists(".env"),
        "Kimi API": "KIMI_API_KEY" in os.environ or os.path.exists(".env"),
    }

    for name, status in checks.items():
        symbol = "[OK]" if status else "[--]"
        print(f"  {symbol} {name}")

    print()


def check_components():
    """检查已安装的组件"""
    print("已安装的组件:")

    components = [
        ("crawl4ai", "Claw 新闻爬虫"),
        ("akshare", "akshare (中国股市数据)"),
        ("fredapi", "fredapi (宏观经济数据)"),
        ("yfinance", "yfinance (美股数据)"),
    ]

    for module, name in components:
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [--] {name}")

    print()


def run_script(script_name):
    """运行 Python 脚本"""
    try:
        print(f"\n启动 {script_name}...")
        print("-" * 70)
        subprocess.run([sys.executable, script_name], check=True)
        return True
    except KeyboardInterrupt:
        print("\n\n用户中断")
        return False
    except Exception as e:
        print(f"\n[错误] 运行失败: {e}")
        return False


def main():
    """主函数"""
    print_banner()

    # 检查 Python
    if not check_python():
        input("按 Enter 键退出...")
        sys.exit(1)

    # 检查环境
    check_env()

    # 检查组件
    check_components()

    # 显示菜单
    print("=" * 70)
    print("           选择启动模式")
    print("=" * 70)
    print()
    print("1. DeepSeek 模式 (推荐) - 性价比最高，稳定可靠")
    print("2. Kimi 模式 - 中文支持最好")
    print("3. Gemini 模式 - 免费，需翻墙")
    print("4. Claw 新闻爬虫模式 - 包含中国新闻爬虫")
    print("5. 测试所有 API 连接")
    print("6. 仅查看配置状态")
    print("0. 退出")
    print()

    while True:
        choice = input("请输入选项 (0-6): ").strip()

        if choice == "1":
            print("\n[启动 DeepSeek 模式]\n")
            run_script("run_with_deepseek.py")
            break

        elif choice == "2":
            print("\n[启动 Kimi 模式]\n")
            run_script("run_with_kimi.py")
            break

        elif choice == "3":
            print("\n[启动 Gemini 模式]")
            print("[注意] Gemini 需要能访问 Google\n")
            run_script("run_with_gemini.py")
            break

        elif choice == "4":
            print("\n[启动 Claw 新闻爬虫模式]\n")
            run_script("run_with_claw_analyst.py")
            break

        elif choice == "5":
            print("\n[测试 API 连接]\n")
            print("测试 DeepSeek...")
            run_script("test_deepseek_simple.py")
            print("\n测试 Kimi...")
            run_script("test_kimi.py")
            print("\n测试 Gemini...")
            run_script("test_gemini_simple.py")
            break

        elif choice == "6":
            print("\n[配置状态]\n")
            check_env()
            check_components()
            continue

        elif choice == "0":
            print("\n退出")
            break

        else:
            print("\n[错误] 无效选项，请重新选择\n")

    input("\n按 Enter 键退出...")


if __name__ == "__main__":
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # 从 .env / 环境变量加载密钥（勿在代码中写死 API Key）
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # 运行主程序
    main()
