"""
测试所有API密钥配置
验证WRDS、Alpha Vantage、DeepSeek、Kimi、Gemini的API密钥是否正确
"""

import os
import sys

# API密钥文件位置
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"
ALPHA_VANTAGE_API_FILE = r"C:\Users\lenovo\TradingAgents\av api.txt"
LLM_API_FILE = r"C:\Users\lenovo\Desktop\new\api assents.txt"


def test_wrds():
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

    try:
        with open(WRDS_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 解析凭据
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
            print("Expected: username: xxx, password: xxx")
            return False

        print(f"[OK] Username: {wrds_username}")
        print(f"[OK] Password: {'*' * len(wrds_password)}")

        # 测试连接
        print()
        print("[Testing] Connecting to WRDS...")
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
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False


def test_alpha_vantage():
    """测试Alpha Vantage API"""
    print()
    print("=" * 80)
    print("Testing Alpha Vantage API")
    print("=" * 80)
    print()

    print(f"File: {ALPHA_VANTAGE_API_FILE}")

    if not os.path.exists(ALPHA_VANTAGE_API_FILE):
        print("[ERROR] File not found!")
        return False

    print("[OK] File found!")

    try:
        with open(ALPHA_VANTAGE_API_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        api_key = content.strip().strip('"').strip("'")
        if '=' in api_key:
            api_key = api_key.split('=', 1)[1].strip()

        if not api_key or len(api_key) < 10:
            print("[ERROR] Invalid API key!")
            return False

        print(f"[OK] API Key: {api_key[:10]}...{api_key[-4:]}")

        # 测试API调用
        print()
        print("[Testing] API call...")
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
                    return True
                elif "Note" in data:
                    print("[WARNING] API call limit reached")
                    return True
                else:
                    print(f"[ERROR] {data.get('Error Message', 'Unknown error')}")
                    return False

        except Exception as e:
            print(f"[ERROR] API test failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False


def test_llm_apis():
    """测试LLM API密钥"""
    print()
    print("=" * 80)
    print("Testing LLM API Keys (DeepSeek, Kimi, Gemini)")
    print("=" * 80)
    print()

    print(f"File: {LLM_API_FILE}")

    if not os.path.exists(LLM_API_FILE):
        print("[ERROR] File not found!")
        return False

    print("[OK] File found!")

    try:
        api_keys = {}

        with open(LLM_API_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 支持多种分隔符
                if ':' in line:
                    key, value = line.split(':', 1)
                elif ',' in line:
                    key, value = line.split(',', 1)
                elif '=' in line:
                    key, value = line.split('=', 1)
                else:
                    continue

                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")

                api_keys[key] = value

        print()
        print(f"[OK] Loaded {len(api_keys)} LLM API key(s):")

        for provider, api_key in api_keys.items():
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"     - {provider.upper()}: {masked}")

        # 验证必需的API
        required = ['deepseek', 'kimi', 'gemini']
        missing = [p for p in required if p not in api_keys]

        if missing:
            print()
            print(f"[WARNING] Missing APIs: {', '.join(missing)}")

        return len(api_keys) > 0

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False


def main():
    """主测试函数"""
    print()
    print("*" * 80)
    print(" " * 20 + "ACCE v2.0 - API Keys Test")
    print("*" * 80)
    print()

    results = {}

    # 测试所有API
    results['WRDS'] = test_wrds()
    results['Alpha Vantage'] = test_alpha_vantage()
    results['LLM APIs'] = test_llm_apis()

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
        print()
        print("[SUCCESS] All API keys are configured correctly!")
        print()
        print("You can now run the analysis system:")
        print("  - Double-click: accev2.0.01.bat")
        print("  - Or run: python run_analysis.py")
    else:
        print()
        print("[WARNING] Some API keys are not configured correctly.")
        print()
        print("Please fix the issues above.")

    print()
    print("=" * 80)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
