"""
新闻情绪分析模式 - 使用DeepSeek AI分析新闻
遇到API限制后自动等待3分钟重试
"""

import os
import sys
import time
from datetime import datetime, timedelta

# 强制设置DeepSeek API密钥
os.environ["OPENAI_API_KEY"] = "sk-61d73d41bcb64482916d75f0709e121b"

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import set_config

# 创建配置 - 只使用新闻数据
config = DEFAULT_CONFIG.copy()

# LLM配置 - 使用DeepSeek
config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"
config["output_language"] = "Chinese"

# 数据源配置 - 只使用新闻（不使用WRDS）
config["data_vendors"] = {
    "core_stock_apis": "yfinance",          # 使用yfinance获取基本数据
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance",                # 新闻数据
}

config["tool_vendors"] = {
    "get_news": "yfinance",
    "get_global_news": "yfinance",
}

# 性能优化配置
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 设置全局配置
set_config(config)

def wait_for_rate_limit(wait_minutes=3):
    """等待API限制解除"""
    print(f"\n{'='*70}")
    print(f"⏸️  遇到API速率限制")
    print(f"{'='*70}")
    print(f"等待时间：{wait_minutes} 分钟")
    print(f"预计恢复时间：{(datetime.now() + timedelta(minutes=wait_minutes)).strftime('%H:%M:%S')}")
    print(f"{'='*70}")

    for i in range(wait_minutes * 60):
        remaining = wait_minutes * 60 - i
        mins, secs = divmod(remaining, 60)

        # 每分钟显示一次进度
        if secs == 0:
            print(f"⏳ 剩余时间: {mins:02d}:{secs:02d}")

        time.sleep(1)

    print(f"\n✅ 等待完成！继续分析...\n")

print("=" * 70)
print("新闻情绪分析模式 (DeepSeek AI)")
print("=" * 70)
print()
print("配置信息:")
print(f"  LLM提供商: DeepSeek (deepseek-chat)")
print(f"  数据源: yfinance 新闻")
print(f"  分析类型: 新闻情绪分析")
print(f"  输出语言: 中文")
print(f"  限制处理: 自动等待3分钟后重试")
print()

try:
    print("正在初始化TradingAgents...")
    ta = TradingAgentsGraph(debug=True, config=config)
    print("✓ 初始化成功！")
    print()

    # 获取用户输入
    ticker = input("请输入股票代码 (例如: AAPL, MSFT, TSLA): ").strip().upper()

    if not ticker:
        ticker = "AAPL"

    print()
    print("=" * 70)
    print(f"正在分析 {ticker} 的新闻和社交媒体情绪")
    print("=" * 70)
    print()
    print("⚠️  注意: yfinance新闻API有速率限制")
    print("如遇到限制，系统会自动等待3分钟后重试")
    print()

    # 运行分析，带有重试机制
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f"正在获取新闻并进行AI分析... (尝试 {retry_count + 1}/{max_retries})")
            print("(这可能需要30-60秒，请耐心等待...)")
            print()

            _, decision = ta.propagate(ticker, datetime.now().strftime("%Y-%m-%d"))

            # 如果成功，显示结果并退出循环
            print()
            print("=" * 70)
            print("📰 新闻分析结果:")
            print("=" * 70)
            print()
            print(decision)
            break

        except Exception as e:
            error_str = str(e)

            # 检查是否是速率限制错误
            if "Rate limited" in error_str or "Too Many Requests" in error_str:
                retry_count += 1

                if retry_count < max_retries:
                    wait_for_rate_limit(wait_minutes=3)
                    # 重试
                    continue
                else:
                    print(f"\n❌ 已达到最大重试次数 ({max_retries} 次)")
                    print(f"建议：稍后再试，或减少查询频率")
                    break
            else:
                # 其他错误，直接显示
                print(f"\n❌ 错误: {type(e).__name__}: {error_str}")
                print("\n故障排除:")
                print("1. 确认DeepSeek API密钥已正确设置")
                print("2. 检查网络连接")
                print("3. 确认股票代码正确 (美股代码)")

                import traceback
                show_debug = input("\n输入 y 查看详细错误信息: ")
                if show_debug.lower() == 'y':
                    print("\n详细错误:")
                    traceback.print_exc()
                break

except KeyboardInterrupt:
    print("\n\n用户取消操作")
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {str(e)}")

print()
print("=" * 70)
print("分析完成")
print("=" * 70)
