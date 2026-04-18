"""
测试 Kimi API（月之暗面）
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

api_key = os.getenv("KIMI_API_KEY")

print("=== 测试 Kimi API ===")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}\n")

try:
    # Kimi 使用 OpenAI 兼容格式
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )

    print("模型: moonshot-v1-8k")
    print("发送测试请求...\n")

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You are a financial analysis assistant"},
            {"role": "user", "content": "What is quantitative trading? Answer in one sentence."}
        ],
        temperature=0.7
    )

    print("[OK] Kimi API connection successful!")
    print(f"\nModel response:\n{response.choices[0].message.content}")

    # 显示 token 使用情况
    print(f"\nTokens used: {response.usage.total_tokens}")

    print("\n[INFO] Kimi API (Moonshot AI)")
    print("[INFO] Base URL: https://api.moonshot.cn/v1")
    print("[INFO] Model: moonshot-v1-8k")
    print("[INFO] Features: Strong Chinese support, 128k context")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")

print("\n=== Test completed ===")
