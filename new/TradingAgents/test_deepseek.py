"""
测试 DeepSeek API 连接
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 测试 DeepSeek API
print("=== 测试 DeepSeek API 连接 ===\n")

# 方案1: 使用 OpenAI SDK (兼容)
try:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )

    print("\n发送测试请求...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个金融分析助手"},
            {"role": "user", "content": "简单介绍一下贵州茅台这家公司"}
        ],
        max_tokens=100
    )

    print("\n✅ DeepSeek API 连接成功！")
    print(f"\n模型回复：\n{response.choices[0].message.content}")

except Exception as e:
    print(f"\n❌ 错误：{e}")
    print("\n请检查：")
    print("1. API Key 是否正确")
    print("2. 网络连接是否正常")
    print("3. DeepSeek API 服务是否可用")

# 方案2: 使用 LangChain (TradingAgents 实际使用的)
print("\n\n=== 测试 LangChain 集成 ===\n")
try:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )

    print("发送测试请求...")
    from langchain_core.messages import HumanMessage

    messages = [HumanMessage(content="用一句话说明什么是量化交易")]
    response = llm.invoke(messages)

    print("\n✅ LangChain + DeepSeek 集成成功！")
    print(f"\n模型回复：\n{response.content}")

except Exception as e:
    print(f"\n❌ LangChain 测试失败：{e}")

print("\n\n=== 测试完成 ===")
