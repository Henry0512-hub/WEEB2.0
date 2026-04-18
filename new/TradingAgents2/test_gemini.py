"""
测试 Google Gemini API（有免费额度）
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 加载环境变量
load_dotenv()

# 从环境变量获取 API Key
api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk")

print("=== 测试 Google Gemini API ===\n")

if not api_key or api_key == "your-gemini-api-key-here":
    print("[ERROR] 请先设置 Gemini API Key")
    print("\n获取步骤：")
    print("1. 访问：https://aistudio.google.com/app/apikey")
    print("2. 创建新的 API Key")
    print("3. 复制 key 并粘贴到本文件的 api_key 变量")
    exit(1)

try:
    # 测试 Gemini 2.5 Flash（免费，快速）
    print("模型: Gemini 2.5 Flash")
    print("免费额度: 每天1500次请求\n")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key,
        temperature=0.7
    )

    print("发送测试请求...")
    from langchain_core.messages import HumanMessage

    messages = [HumanMessage(content="什么是量化交易？用一句话回答。")]
    response = llm.invoke(messages)

    print(f"\n[OK] Gemini API 连接成功！")
    print(f"\n模型回复：\n{response.content}")

except Exception as e:
    print(f"\n[ERROR] 测试失败：{e}")
    print("\n可能的原因：")
    print("1. API Key 无效")
    print("2. 网络连接问题（需要能访问 Google）")
    print("3. 未启用 Gemini API")

# Gemini 模型列表
print("\n\n=== Gemini 免费模型 ===")
print("✅ gemini-2.5-flash - 最新，快速（推荐）")
print("✅ gemini-2.5-flash-lite - 更轻量，更便宜")
print("✅ gemini-2.5-pro - 更强推理（也在免费额度内）")
print("✅ gemini-1.5-flash - 稳定版本")

print("\n=== 免费额度 ===")
print("- 每天：1,500 次请求")
print("- 每月：免费可用相当慷慨")
print("- 适合：个人使用、测试、学习")

print("\n=== 获取 API Key ===")
print("1. 访问：https://aistudio.google.com/app/apikey")
print("2. 点击 'Create API Key'")
print("3. 复制 key 到本文件或 .env 文件")
