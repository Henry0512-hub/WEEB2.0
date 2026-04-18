#!/usr/bin/env python3
"""
当前模型可用性检测
- 当前对话模型
- 项目配置的 LLM 模型 (DeepSeek, Kimi, Gemini)
"""

print("=== 当前对话模型 ===")
print("当前跟你对话的模型: **Codex 5.3**\n")
print("=== 项目配置的外部 LLM 模型测试 (美西VPN) ===\n")

import os
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

keys = {
    "deepseek": "sk-ac15509d87f5410cb2e82dbc70f7a395",
    "kimi": "sk-zuVM5fhu24KzBytPVhcz8lF6k37GNqXnZcQRAwgfj3GBeN53",
    "gemini": "AIzaSyDaxsuXUwRNVVmZKRi2tzdo6WvaelpNCeY"
}

success = {}

# 测试 DeepSeek
print("1. DeepSeek (deepseek-chat)")
try:
    client = OpenAI(
        api_key=keys["deepseek"],
        base_url="https://api.deepseek.com/v1",
        timeout=15
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "请回复一个'OK'"}],
        max_tokens=10,
        temperature=0.1
    )
    print("   [OK] 可用 - DeepSeek-V3 正常")
    success["deepseek"] = True
except Exception as e:
    print(f"   [FAIL] 不可用 - {type(e).__name__}: {str(e)[:60]}")
    success["deepseek"] = False

# 测试 Kimi
print("\n2. Kimi (moonshot-v1-8k)")
try:
    client = OpenAI(
        api_key=keys["kimi"],
        base_url="https://api.moonshot.cn/v1",
        timeout=15
    )
    resp = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": "请回复一个'OK'"}],
        max_tokens=10,
        temperature=0.1
    )
    print("   [OK] 可用 - Kimi 正常")
    success["kimi"] = True
except Exception as e:
    print(f"   [FAIL] 不可用 - {type(e).__name__}: {str(e)[:60]}")
    success["kimi"] = False

# 测试 Gemini
print("\n3. Gemini (gemini-2.5-flash)")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=keys["gemini"],
        temperature=0.1,
        timeout=15
    )
    resp = llm.invoke([HumanMessage(content="请回复一个'OK'")])
    print("   [OK] 可用 - Gemini 2.5 Flash 正常")
    success["gemini"] = True
except Exception as e:
    print(f"   [FAIL] 不可用 - {type(e).__name__}: {str(e)[:60]}")
    success["gemini"] = False

print("\n" + "="*70)
print("最终结果:")
print(f"• 当前跟你对话的模型: **Codex 5.3**")
print(f"• DeepSeek: {'✅ 可用' if success.get('deepseek') else '❌ 不可用'}")
print(f"• Kimi:     {'✅ 可用' if success.get('kimi') else '❌ 不可用'}")
print(f"• Gemini:   {'✅ 可用' if success.get('gemini') else '❌ 不可用'}")
print("="*70)
print("\n推荐：")
print("在当前网络环境下，**DeepSeek** 通常是最稳定且性价比最高的选项。")
