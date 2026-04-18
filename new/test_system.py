"""
ACCE v2.0 - 系统测试
验证所有组件是否正常工作
"""

import os
import sys
from datetime import datetime

# 测试配置
PYTHON_VERSION = sys.version
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"
WORK_DIR = r"C:\Users\lenovo\Desktop\new"


def test_python_version():
    """测试Python版本"""
    print("=" * 80)
    print("Testing Python Version")
    print("=" * 80)
    print(f"Python Version: {PYTHON_VERSION}")
    print(f"Python Executable: {sys.executable}")

    version_parts = PYTHON_VERSION.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])

    if major >= 3 and minor >= 8:
        print("[OK] Python version is compatible")
        return True
    else:
        print("[WARNING] Python version may not be compatible")
        print("         Recommended: Python 3.8+")
        return False


def test_dependencies():
    """测试依赖包"""
    print("\n" + "=" * 80)
    print("Testing Dependencies")
    print("=" * 80)

    required_modules = [
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
        ('yfinance', 'Yahoo Finance API'),
        ('requests', 'HTTP requests'),
    ]

    optional_modules = [
        ('wrds', 'WRDS database'),
        ('akshare', 'Chinese stocks'),
        ('dotenv', 'Environment variables'),
    ]

    all_ok = True

    print("\n[Required Modules]")
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"  [OK] {module:15} - {description}")
        except ImportError:
            print(f"  [MISSING] {module:15} - {description}")
            all_ok = False

    print("\n[Optional Modules]")
    for module, description in optional_modules:
        try:
            if module == 'dotenv':
                __import__('dotenv')
            else:
                __import__(module)
            print(f"  [OK] {module:15} - {description}")
        except ImportError:
            print(f"  [INFO] {module:15} - {description} (not installed)")

    return all_ok


def test_wrds_credentials():
    """测试WRDS凭据"""
    print("\n" + "=" * 80)
    print("Testing WRDS Credentials")
    print("=" * 80)

    print(f"\nLooking for: {WRDS_CREDENTIALS_FILE}")

    if not os.path.exists(WRDS_CREDENTIALS_FILE):
        print("[WARNING] WRDS credentials file not found")
        print("\nTo use WRDS, create the file with:")
        print(f"  Location: {WRDS_CREDENTIALS_FILE}")
        print("  Format:")
        print("    username=your_wrds_username")
        print("    password=your_wrds_password")
        return False

    print("[OK] WRDS credentials file found")

    try:
        with open(WRDS_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 2:
            print("[ERROR] File must contain at least 2 lines")
            return False

        username = lines[0].strip().split('=')[1].strip() if '=' in lines[0] else lines[0].strip()
        password = lines[1].strip().split('=')[1].strip() if '=' in lines[1] else lines[1].strip()

        print(f"[OK] Username: {username}")
        print(f"[OK] Password: {'*' * len(password)}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to read credentials: {e}")
        return False


def test_data_fetcher():
    """测试数据获取器"""
    print("\n" + "=" * 80)
    print("Testing Data Fetcher")
    print("=" * 80)

    try:
        # 添加工作目录到路径
        sys.path.insert(0, WORK_DIR)
        from intelligent_data_fetcher import IntelligentDataFetcher

        print("[OK] Intelligent data fetcher imported successfully")

        # 测试WRDS优先级判断
        print("\n[Testing WRDS Priority Logic]")

        test_cases = [
            ("AAPL", "2024-06-15", "2024-08-15", True, "US stock historical data"),
            ("TSLA", "2025-01-15", "2025-03-20", False, "US stock recent data"),
            ("BABA", "2024-06-01", "2024-08-01", False, "Chinese stock"),
        ]

        all_ok = True
        for ticker, start, end, should_use, reason in test_cases:
            fetcher = IntelligentDataFetcher(ticker, start, end)
            result = fetcher._should_use_wrds()

            status = "[OK]" if result == should_use else "[ERROR]"
            print(f"  {status} {ticker:10} {start:10} -> {end:10} WRDS={result} ({reason})")

            if result != should_use:
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"[ERROR] Data fetcher test failed: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 80)
    print("Testing File Structure")
    print("=" * 80)

    required_files = [
        (WORK_DIR, "Working directory"),
        (os.path.join(WORK_DIR, "intelligent_data_fetcher.py"), "Data fetcher"),
        (os.path.join(WORK_DIR, "run_analysis.py"), "Main program"),
        (os.path.join(WORK_DIR, "test_wrds.py"), "WRDS test"),
        (os.path.join(WORK_DIR, "README.md"), "Documentation"),
    ]

    all_ok = True
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"  [OK] {description:20} - {file_path}")
        else:
            print(f"  [ERROR] {description:20} - {file_path}")
            all_ok = False

    return all_ok


def main():
    """主测试函数"""
    print("\n")
    print("*" * 80)
    print(" " * 20 + "ACCE v2.0 - System Test")
    print("*" * 80)
    print()

    results = {}

    # 运行所有测试
    results['Python Version'] = test_python_version()
    results['Dependencies'] = test_dependencies()
    results['File Structure'] = test_file_structure()
    results['WRDS Credentials'] = test_wrds_credentials()
    results['Data Fetcher'] = test_data_fetcher()

    # 打印总结
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 80)

    all_passed = all(results.values())

    if all_passed:
        print("\n[SUCCESS] All tests passed! System is ready to use.")
        print("\nTo start the system:")
        print("  1. Double-click: accev2.0.01.bat")
        print("  2. Or run: python run_analysis.py")
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        print("\nRequired actions:")
        if not results['Dependencies']:
            print("  - Install missing packages: pip install pandas numpy yfinance requests")
        if not results['WRDS Credentials']:
            print("  - Create WRDS credentials file (see details above)")

    print("\n" + "=" * 80)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
