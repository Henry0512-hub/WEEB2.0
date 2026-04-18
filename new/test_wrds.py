"""
测试WRDS连接
验证系统能否正确读取固定位置的WRDS凭据
"""

import os
import sys

# 固定WRDS凭据文件位置
WRDS_CREDENTIALS_FILE = r"C:\Users\lenovo\TradingAgents\id.txt"


def test_wrds_credentials():
    """测试WRDS凭据读取"""
    print("=" * 80)
    print("WRDS Credentials Test")
    print("=" * 80)
    print()

    print(f"Looking for WRDS credentials at:")
    print(f"  {WRDS_CREDENTIALS_FILE}")
    print()

    # 检查文件是否存在
    if not os.path.exists(WRDS_CREDENTIALS_FILE):
        print("[ERROR] WRDS credentials file NOT found!")
        print()
        print("Please create the file with the following format:")
        print(f"  Location: {WRDS_CREDENTIALS_FILE}")
        print("  Content:")
        print("    username=your_wrds_username")
        print("    password=your_wrds_password")
        print()
        input("Press Enter to exit...")
        return False

    print("[OK] WRDS credentials file found!")
    print()

    # 读取凭据
    try:
        with open(WRDS_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 2:
            print("[ERROR] File must contain at least 2 lines (username and password)")
            input("Press Enter to exit...")
            return False

        # Parse credentials - support both "=" and ":" separators
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
            print("[ERROR] Invalid credentials format")
            print("Expected format:")
            print("  username: your_username")
            print("  password: your_password")
            input("Press Enter to exit...")
            return False

        print(f"[OK] Username: {wrds_username}")
        print(f"[OK] Password: {'*' * len(wrds_password)}")
        print()

    except Exception as e:
        print(f"[ERROR] Failed to read credentials: {e}")
        input("Press Enter to exit...")
        return False

    # 尝试连接WRDS
    print("=" * 80)
    print("Testing WRDS Connection...")
    print("=" * 80)
    print()

    try:
        import wrds

        print("[INFO] Connecting to WRDS...")
        db = wrds.Connection(wrds_username=wrds_username, wrds_password=wrds_password)

        print("[OK] Successfully connected to WRDS!")
        print()

        # 测试查询
        print("[INFO] Testing a simple query...")
        result = db.get_sql('SELECT COUNT(*) FROM crsp.dsf')
        print(f"[OK] Query result: {result}")
        print()

        db.close()
        print("[SUCCESS] WRDS connection test PASSED!")
        print()
        print("Your WRDS credentials are working correctly.")
        print("The system can now use WRDS for historical stock data.")

    except ImportError:
        print("[WARNING] wrds module not installed")
        print()
        print("To install wrds, run:")
        print("  pip install wrds")
        print()
        print("However, the system will use other data sources as fallback.")

    except Exception as e:
        print(f"[ERROR] WRDS connection failed: {e}")
        print()
        print("Possible reasons:")
        print("  1. Wrong username or password")
        print("  2. Network connection issue")
        print("  3. WRDS account not activated")
        print()
        print("However, the system will use other data sources as fallback.")

    print()
    print("=" * 80)
    input("Press Enter to exit...")
    return True


if __name__ == "__main__":
    test_wrds_credentials()
