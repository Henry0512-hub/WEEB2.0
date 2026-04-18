# -*- coding: utf-8 -*-
"""
测试API密钥是否有效
"""
import sys
import os

print("="*70)
print("API密钥测试")
print("="*70)
print()

# 测试1: 读取配置文件
print("[测试1] 读取API配置...")
try:
    from api_config import DEEPSEEK_API_KEY
    if DEEPSEEK_API_KEY:
        print(f"[成功] API密钥已加载: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-4:]}")
    else:
        print("[失败] API密钥为空")
        sys.exit(1)
except ImportError as e:
    print(f"[失败] 无法导入配置: {e}")
    print("提示: 请确保api_config.py文件存在")
    sys.exit(1)

print()

# 测试2: 测试DeepSeek API连接
print("[测试2] 测试DeepSeek API连接...")
try:
    from openai import OpenAI

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )

    # 发送一个简单的测试请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "你好，请回复OK"}
        ],
        max_tokens=10
    )

    result = response.choices[0].message.content
    print(f"[成功] API响应: {result}")

except Exception as e:
    print(f"[失败] API错误: {e}")
    print()
    print("可能的原因:")
    print("1. API密钥无效或已过期")
    print("2. API余额不足")
    print("3. 网络连接问题")
    print("4. API服务暂时不可用")
    sys.exit(1)

print()

# 测试3: 检查余额（如果API支持）
print("[测试3] API密钥信息:")
print(f"密钥长度: {len(DEEPSEEK_API_KEY)} 字符")
print(f"密钥前缀: {DEEPSEEK_API_KEY[:10]}")
print(f"密钥后缀: {DEEPSEEK_API_KEY[-4:]}")

print()
print("="*70)
print("测试完成！API密钥工作正常")
print("="*70)
print()
print("现在可以使用以下命令启动系统:")
print("  python run_crypto_trading.py")
print()
