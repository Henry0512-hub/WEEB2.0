"""
测试WRDS账户连接
"""
import wrds

# 测试连接
print("测试WRDS连接...")
print(f"用户名: hengyang24")

try:
    db = wrds.Connection(wrds_username='hengyang24', wrds_password='Appleoppo17@')
    print("连接成功！")
    print(f"账户已激活")

    # 测试简单查询
    print("\n测试查询...")
    result = db.list_tables(library='crsp')
    print(f"可以访问CRSP数据库")
    print(f"查询到 {len(result)} 个表")

    db.close()
    print("\nWRDS账户完全正常！")

except Exception as e:
    print(f"\n连接失败")
    print(f"错误: {e}")
    print(f"\n可能的原因:")
    print(f"1. 账户未在WRDS网站激活")
    print(f"2. 用户名或密码错误")
    print(f"3. 网络连接问题")
    print(f"\n建议:")
    print(f"请访问 https://wrds.wharton.upenn.edu/")
    print(f"使用账户登录一次，然后重试")
