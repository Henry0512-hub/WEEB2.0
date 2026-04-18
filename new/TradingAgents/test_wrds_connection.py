"""
测试WRDS连接 - 使用id.txt中的账号密码
"""

import wrds
import os
from pathlib import Path

# 读取id.txt获取凭据
id_file = Path(__file__).parent / "id.txt"
with open(id_file, 'r') as f:
    lines = f.readlines()
    username = lines[0].strip().split(': ')[1]
    password = lines[1].strip().split(': ')[1]

print("="*70)
print("WRDS Connection Test")
print("="*70)
print(f"\nUsername: {username}")
print(f"Password: {'*' * len(password)}")
print()

# 方法1: 创建.pgpass文件（推荐方法）
print("[Method 1] Creating .pgpass file...")

home = Path.home()
pgpass_file = home / ".pgpass"

# WRDS连接信息 - 格式: hostname:port:database:username:password
# 注意：WRDS用户名通常是完整的用户名，不是hg244
pgpass_content = f"wrds-pgdata.wharton.upenn.edu:9737:wrds:{username}:{password}\n"

try:
    # 创建.pgpass文件
    with open(pgpass_file, 'w') as f:
        f.write(pgpass_content)

    # 设置权限（Windows可能不支持，但尝试设置）
    try:
        os.chmod(pgpass_file, 0o600)
    except:
        pass

    print(f"[Created] .pgpass file: {pgpass_file}")

    # 使用.pgpass连接
    print("\n[Connecting] Connecting to WRDS...")
    db = wrds.Connection(wrds_username=username)
    print("[Success] WRDS connection successful!")

    # 测试查询
    print("\n[Test] Querying AAPL stock info...")
    test_sql = """
    SELECT permno, ticker, comnam
    FROM crsp.stocknames
    WHERE ticker = 'AAPL'
    LIMIT 1
    """
    result = db.raw_sql(test_sql)
    print(f"[Success] Query successful! Found {len(result)} records")
    print(result)

    # 测试查询历史价格数据
    print("\n[Test 2] Querying AAPL historical prices (2024-06-15 to 2024-08-15)...")
    price_sql = """
    SELECT date, permno, prc AS close, vol AS volume
    FROM crsp.dsf
    WHERE permno = (SELECT permno FROM crsp.stocknames WHERE ticker = 'AAPL' ORDER BY namedt DESC LIMIT 1)
    AND date >= '2024-06-15'
    AND date <= '2024-08-15'
    ORDER BY date
    """
    price_data = db.raw_sql(price_sql, date_cols=['date'])
    print(f"[Success] Found {len(price_data)} price records")
    print(f"Date range: {price_data['date'].min()} to {price_data['date'].max()}")
    print(f"Price range: ${price_data['close'].min():.2f} - ${price_data['close'].max():.2f}")

    db.close()
    print("\n[Closed] WRDS connection closed")

except Exception as e:
    print(f"[Failed] Connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Test Complete")
print("="*70)
