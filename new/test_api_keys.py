"""
测试API密钥配置
验证系统能否正确读取所有API密钥
"""

import os
import sys

# API密钥文件位置
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"
ALPHA_VANTAGE_API_FILE = r"C:\Users\lenovo\TradingAgents\av api.txt"


def test_wrds_credentials():
    """测试WRDS凭据"""
    print("=" * 80)
    print("Testing WRDS Credentials")
    print("=" * 80)
    print()

    print(f"File: {WRDS_CREDENTIALS_FILE}")

    if not os.path.exists(WRDS_CREDENTIALS_FILE):
        print("[ERROR] File not found!")
        return False

    print("[OK] File found!")
    print()

    try:
        with open(WRDS_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Parse credentials
        wrds_username = None
        wrds_password = None

        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                if key == 'username':
                    wrds_username = value.strip()
                elif key == 'password':
                    wrds_password = value.strip()
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                if key == 'username':
                    wrds_username = value.strip()
                elif key == 'password':
                    wrds_password = value.strip()

        if not wrds_username or not wrds_password:
            print("[ERROR] Invalid format!")
            print("Expected format:")
            print("  username: your_username")
            print("  password: your_password")
            return False

        print(f"[OK] Username: {wrds_username}")
        print(f"[OK] Password: {'*' * len(wrds_password)}")
        print()

        # Test connection
        print("Testing WRDS connection...")
        try:
            import wrds
            db = wrds.Connection(
                wrds_username=wrds_username,
                wrds_password=wrds_password,
                autoconnect=True,
            )
            print("[OK] Successfully connected to WRDS!")
            db.close()
            return True
        except ImportError:
            print("[INFO] wrds module not installed")
            print("       Install: pip install wrds")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return False


def test_alpha_vantage_api():
    """测试Alpha Vantage API密钥"""
    print()
    print("=" * 80)
    print("Testing Alpha Vantage API Key")
    print("=" * 80)
    print()

    print(f"File: {ALPHA_VANTAGE_API_FILE}")

    if not os.path.exists(ALPHA_VANTAGE_API_FILE):
        print("[ERROR] File not found!")
        return False

    print("[OK] File found!")
    print()

    try:
        with open(ALPHA_VANTAGE_API_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Remove whitespace, quotes, or "api_key=" prefix
        api_key = content.strip().strip('"').strip("'")
        if '=' in api_key:
            api_key = api_key.split('=', 1)[1].strip()

        if not api_key or len(api_key) < 10:
            print("[ERROR] Invalid API key format!")
            print("Expected format:")
            print("  01D7TZIVI5LPD54Z")
            return False

        print(f"[OK] API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"[OK] Length: {len(api_key)} characters")
        print()

        # Test API call
        print("Testing Alpha Vantage API...")
        try:
            import requests
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": "IBM",
                "apikey": api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if "Time Series (Daily)" in data:
                    print("[OK] API key is valid!")
                    print("[OK] Successfully fetched test data!")
                    return True
                elif "Note" in data:
                    print("[WARNING] API call limit reached")
                    print("          (This is normal for free tier)")
                    return True
                elif "Error Message" in data:
                    print(f"[ERROR] Invalid API key: {data['Error Message']}")
                    return False
            else:
                print(f"[ERROR] HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] API test failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return False


def main():
    """主测试函数"""
    print("\n")
    print("*" * 80)
    print(" " * 25 + "API Keys Test")
    print("*" * 80)
    print()

    results = {}

    # 测试所有API密钥
    results['WRDS Credentials'] = test_wrds_credentials()
    results['Alpha Vantage API'] = test_alpha_vantage_api()

    # 打印总结
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    print()
    print("=" * 80)

    all_passed = all(results.values())

    if all_passed:
        print("\n[SUCCESS] All API keys are configured correctly!")
        print("\nYou can now run the analysis system:")
        print("  - Double-click: accev2.0.01.bat")
        print("  - Or run: python run_analysis.py")
    else:
        print("\n[WARNING] Some API keys are not configured correctly.")
        print("\nPlease check the errors above and fix the issues.")

    print()
    print("=" * 80)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
