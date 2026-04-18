"""
测试 DeepSeek API 连接（简化版）
"""
import os
from openai import OpenAI

api_key = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"

print("=== 测试 DeepSeek API ===")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )

    print("\n发送测试请求...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a financial analysis assistant"},
            {"role": "user", "content": "What is quantitative trading? Answer in one sentence."}
        ],
        max_tokens=100
    )

    print("\n[OK] DeepSeek API connection successful!")
    print(f"\nModel response:\n{response.choices[0].message.content}")

    # 显示 token 使用情况
    print(f"\nTokens used: {response.usage.total_tokens}")

except Exception as e:
    print(f"\n[ERROR] {e}")
