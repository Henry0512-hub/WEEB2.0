"""
Gemini API 自动配置脚本
运行后输入你的 Gemini API Key 即可自动配置
"""
import os
from pathlib import Path

print("="*60)
print("   TradingAgents - Gemini API 配置向导")
print("="*60)

print("\n[提示] 如果还没有 Gemini API Key，请先访问：")
print("       https://aistudio.google.com/app/apikey\n")

# 获取 API Key
api_key = input("请输入你的 Gemini API Key: ").strip()

if not api_key:
    print("\n[错误] API Key 不能为空")
    exit(1)

if not api_key.startswith("AIza"):
    print("\n[警告] API Key 格式似乎不正确（通常以 AIza 开头）")
    confirm = input("是否继续？(y/n): ").lower()
    if confirm != 'y':
        exit(1)

# 更新 .env 文件
env_path = Path(__file__).parent / ".env"
env_content = ""

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()

# 检查是否已有 GOOGLE_API_KEY
if "GOOGLE_API_KEY=" in env_content:
    print("\n[信息] .env 文件中已存在 GOOGLE_API_KEY")
    choice = input("是否覆盖？(y/n): ").lower()
    if choice != 'y':
        print("\n[取消] 配置已取消")
        exit(0)

# 更新或添加 GOOGLE_API_KEY
lines = env_content.split('\n')
new_lines = []
key_added = False

for line in lines:
    if line.startswith("GOOGLE_API_KEY="):
        new_lines.append(f"GOOGLE_API_KEY={api_key}")
        key_added = True
    elif line.startswith("#") and "GOOGLE_API_KEY" in line:
        # 保留注释行
        new_lines.append(line)
    else:
        new_lines.append(line)

if not key_added:
    new_lines.append(f"\n# Gemini API Key")
    new_lines.append(f"GOOGLE_API_KEY={api_key}")

# 写入 .env 文件
with open(env_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print(f"\n[成功] API Key 已保存到 .env 文件")
print(f"       文件路径: {env_path}")

# 创建 Gemini 配置文件
config_content = '''"""
Gemini API 配置
用于 TradingAgents 框架
"""

from tradingagents.default_config import DEFAULT_CONFIG

# Gemini API 配置
GEMINI_CONFIG = DEFAULT_CONFIG.copy()

# LLM 提供商设置为 Google
GEMINI_CONFIG["llm_provider"] = "google"

# Gemini 模型配置
GEMINI_CONFIG["deep_think_llm"] = "gemini-2.5-flash"      # 主要推理模型（免费）
GEMINI_CONFIG["quick_think_llm"] = "gemini-2.5-flash-lite"  # 快速任务模型（更便宜）

# 可选：使用更强的模型
# GEMINI_CONFIG["deep_think_llm"] = "gemini-2.5-pro"

# 其他配置
GEMINI_CONFIG["max_debate_rounds"] = 1
GEMINI_CONFIG["max_risk_discuss_rounds"] = 1
GEMINI_CONFIG["output_language"] = "Chinese"  # 输出中文

# 数据源配置
GEMINI_CONFIG["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",
}

# 使用示例
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    # 加载环境变量
    load_dotenv()

    # 检查 API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[错误] 未找到 GOOGLE_API_KEY，请运行 setup_gemini.py 配置")
        exit(1)

    print(f"[成功] Gemini API Key 已加载: {api_key[:10]}...{api_key[-4:]}")

    # 创建 TradingAgents 实例
    ta = TradingAgentsGraph(debug=True, config=GEMINI_CONFIG)

    # 运行分析（示例：阿里巴巴）
    ticker = "BABA"
    date = "2025-01-15"

    print(f"\\n开始分析 {ticker}...")
    _, decision = ta.propagate(ticker, date)

    print(f"\\n=== 最终决策 ===")
    print(decision)
'''

config_path = Path(__file__).parent / "gemini_config.py"
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)

print(f"\n[成功] 已创建配置文件: {config_path}")

# 显示免费额度信息
print("\n" + "="*60)
print("   Gemini 免费额度信息")
print("="*60)
print("✅ 每天：1,500 次请求")
print("✅ 每月：慷慨的免费额度")
print("✅ 模型：Gemini 2.5 Flash, Flash Lite, Pro")
print("✅ 适合：个人使用、测试、学习")

print("\n" + "="*60)
print("   下一步")
print("="*60)
print("1. 测试 API 连接：")
print("   python test_gemini.py")
print("\n2. 运行示例：")
print("   python run_with_gemini.py")
print("\n3. 使用 CLI：")
print("   tradingagents")
print("   然后选择 Google 作为 LLM Provider")

print("\n[完成] Gemini API 配置完成！")
'''

# 显示配置信息
print("\n" + "="*60)
print("   配置总结")
print("="*60)
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print(f"Provider: Google (Gemini)")
print(f"模型: gemini-2.5-flash")
print(f"免费额度: 每天 1,500 次请求")

print("\n[提示] 如果需要科学上网访问 Google API")
print("       可以考虑使用 DeepSeek 或国产大模型作为替代")
