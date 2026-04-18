"""
轻量级加密货币分析 - 使用DeepSeek AI
不使用TradingAgentsGraph，直接调用API
"""

import os
import sys
import time
from datetime import datetime

# 强制设置DeepSeek API密钥
os.environ["OPENAI_API_KEY"] = "sk-61d73d41bcb64482916d75f0709e121b"

# 尝试导入OpenAI (DeepSeek兼容)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://api.deepseek.com/v1")
    USE_DEEPSEEK = True
    print("✓ DeepSeek API已连接")
except Exception as e:
    print(f"⚠️  无法连接DeepSeek API: {e}")
    print("将使用基础模式...")
    USE_DEEPSEEK = False

# 导入CoinGecko
try:
    from tradingagents.dataflows.coingecko_source import get_coingecko_stock_data
    COINGECKO_AVAILABLE = True
    print("✓ CoinGecko数据源已加载")
except ImportError:
    print("⚠️  CoinGecko模块未找到")
    COINGECKO_AVAILABLE = False

def get_crypto_data_simple(symbol):
    """简化版加密货币数据获取"""
    if not COINGECKO_AVAILABLE:
        return None

    try:
        # 获取当前日期和30天前
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # 获取数据
        result = get_coingecko_stock_data(symbol, start_date, end_date)

        if "Error" in result:
            return None

        return result
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def analyze_with_deepseek(symbol, data):
    """使用DeepSeek分析数据"""
    if not USE_DEEPSEEK:
        return "AI分析不可用 - 请检查DeepSeek API配置"

    try:
        prompt = f"""请分析以下加密货币数据并给出投资建议：

加密货币: {symbol}
数据时间范围: 最近30天

数据摘要:
{data[:1000] if len(data) > 1000 else data}

请提供:
1. 价格趋势分析
2. 技术指标解读
3. 风险评估
4. 投资建议(买入/卖出/持有)
5. 目标价位(如果适用)

请用中文回答，格式清晰。"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的加密货币分析师，擅长技术分析和市场情绪判断。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI分析失败: {str(e)}"

def main():
    print("=" * 70)
    print("轻量级加密货币分析 (DeepSeek AI)")
    print("=" * 70)
    print()

    # 获取用户输入
    symbol = input("请输入加密货币代码 (例如: BTC, ETH, SOL): ").strip().upper()

    if not symbol:
        symbol = "BTC"
        print(f"默认使用: {symbol}")

    if symbol.lower() == 'q':
        print("退出")
        return

    print()
    print(f"正在获取 {symbol} 的数据...")

    # 获取数据
    data = get_crypto_data_simple(symbol)

    if not data:
        print(f"❌ 无法获取 {symbol} 的数据")
        print()
        print("可能的原因:")
        print("1. CoinGecko API限制 (免费版: 50次/分钟)")
        print("2. 加密货币代码不正确")
        print("3. 网络连接问题")
        print()
        print("建议:")
        print("- 等待几分钟后重试")
        print("- 使用主流币种 (BTC, ETH, SOL等)")
        print("- 考虑使用WRDS分析美股")
        return

    print(f"✓ 数据获取成功")
    print()

    # 使用DeepSeek分析
    if USE_DEEPSEEK:
        print("正在使用DeepSeek AI分析...")
        print("(这可能需要30-60秒)")
        print()

        analysis = analyze_with_deepseek(symbol, data)

        print()
        print("=" * 70)
        print(f"📊 {symbol} 分析报告")
        print("=" * 70)
        print()
        print(analysis)
    else:
        # 显示原始数据
        print("=" * 70)
        print(f"📊 {symbol} 数据")
        print("=" * 70)
        print()
        print(data[:2000])

    print()
    print("=" * 70)
    print("分析完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
