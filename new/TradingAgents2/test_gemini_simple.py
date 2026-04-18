"""
测试 Gemini API 连接（简化版）
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 加载环境变量
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("=== 测试 Gemini API ===")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}\n")

try:
    # 测试 Gemini 2.5 Flash
    print("模型: Gemini 2.5 Flash")
    print("免费额度: 每天 1500 次请求\n")

    print("发送测试请求...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key,
        temperature=0.7
    )

    from langchain_core.messages import HumanMessage

    messages = [HumanMessage(content="What is quantitative trading? Answer in one sentence.")]
    response = llm.invoke(messages)

    print("\n[OK] Gemini API connection successful!")
    print(f"\nModel response:\n{response.content}")

    # 显示模型信息
    print("\n[INFO] Model: gemini-2.5-flash")
    print("[INFO] Free tier: 1,500 requests per day")
    print("[INFO] Provider: Google")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")

    print("\nPossible reasons:")
    print("1. Cannot access Google API (need VPN)")
    print("2. Invalid API Key")
    print("3. Rate limit exceeded")

    print("\nSuggestions:")
    print("- Use DeepSeek as alternative (already configured)")
    print("- Check network connection")
    print("- Verify API Key is correct")

print("\n=== Test completed ===")
