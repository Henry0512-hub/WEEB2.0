"""
加密货币交易分析脚本

专门为加密货币市场设计的多智能体分析系统
支持BTC、ETH等主流加密货币的交易分析

使用方法：
python run_crypto_trading.py
"""

import os
import sys
import io

# 设置UTF-8编码输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.smart_router import get_smart_config
from tradingagents.utils.trading_signal import display_trading_recommendation

# 加载环境变量
load_dotenv()

# 从配置文件加载API密钥
try:
    from api_config import DEEPSEEK_API_KEY
    # 使用配置文件中的API密钥
    os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY
    print(f"[配置] 已加载API密钥: {DEEPSEEK_API_KEY[:10]}...")
except ImportError:
    print("[警告] 未找到api_config.py，使用默认密钥")
    DEEPSEEK_API_KEY = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"
    os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY


def show_crypto_reference():
    """显示加密货币代码参考"""
    print()
    print("="*70)
    print("[加密货币] 加密货币代码参考")
    print("="*70)
    print()
    print("[主流] 主流加密货币:")
    print("  BTC    - 比特币 (Bitcoin) - 市值第一")
    print("  ETH    - 以太坊 (Ethereum) - 智能合约平台")
    print("  BNB    - 币安币 (Binance Coin) - 交易所平台币")
    print("  SOL    - Solana - 高性能区块链")
    print("  XRP    - 瑞波币 (XRP) - 跨境支付")
    print()
    print("[公链] 热门公链:")
    print("  ADA    - 艾达币 (Cardano)")
    print("  AVAX   - Avalanche")
    print("  DOT    - 波卡 (Polkadot)")
    print("  MATIC  - Polygon")
    print("  ATOM   - Cosmos")
    print()
    print("[DeFi] DeFi 代币:")
    print("  UNI    - Uniswap - DEX协议")
    print("  AAVE   - Aave - 借贷协议")
    print("  LINK   - Chainlink - 预言机")
    print("  COMP   - Compound")
    print()
    print("[Meme] Meme币:")
    print("  DOGE   - 狗狗币 (Dogecoin)")
    print("  SHIB   - 柴犬币 (Shiba Inu)")
    print("  PEPE   - Pepe")
    print("  WIF    - dogwifhat")
    print()
    print("[其他] 其他热门:")
    print("  OP     - Optimism - L2解决方案")
    print("  ARB    - Arbitrum - L2解决方案")
    print("  INJ    - Injective")
    print("  FET    - Fetch.ai")
    print("  RNDR   - Render")
    print()
    print("="*70)
    print()


def analyze_crypto(ticker, date):
    """
    分析单个加密货币

    Args:
        ticker: 加密货币代码
        date: 分析日期

    Returns:
        bool: 分析是否成功
    """
    print()
    print("="*70)
    print(f"开始分析: {ticker}")
    print(f"分析日期: {date}")
    print("="*70)
    print()

    # 配置 TradingAgents 使用 DeepSeek
    config = DEFAULT_CONFIG.copy()

    # DeepSeek 配置（使用 OpenAI 兼容模式）
    config["llm_provider"] = "openai"
    config["backend_url"] = "https://api.deepseek.com/v1"
    config["deep_think_llm"] = "deepseek-chat"
    config["quick_think_llm"] = "deepseek-chat"

    # 输出语言设置为中文
    config["output_language"] = "Chinese"

    # 辩论轮数（降低可以节省 API 调用）
    config["max_debate_rounds"] = 1
    config["max_risk_discuss_rounds"] = 1

    # 数据源配置 - 优先使用CoinGecko
    config["data_vendors"] = {
        "core_stock_apis": "coingecko",
        "technical_indicators": "yfinance",
        "fundamental_data": "coingecko",
        "news_data": "yfinance",
    }

    # 智能数据源路由
    config = get_smart_config(ticker, config)

    print("[INFO] 初始化加密货币交易分析系统（使用 DeepSeek）...")
    print("[INFO] 多智能体分析系统启动中...")
    print()

    # 显示智能体列表
    print("智能体团队:")
    print("  [+] 市场分析师 - 分析价格趋势和技术指标")
    print("  [+] 社交媒体分析师 - 分析社区情绪")
    print("  [+] 新闻分析师 - 分析行业新闻")
    print("  [+] 基本面分析师 - 分析链上数据和项目基本面")
    print("  [+] 研究员团队 - 辩论分析")
    print("  [+] 交易员 - 制定交易策略")
    print("  [+] 风险管理团队 - 评估风险")
    print("  [+] 投资组合经理 - 最终决策")
    print()
    print("[等待] 请稍候，这可能需要几分钟...")
    print()

    try:
        # 创建 TradingAgents 实例
        ta = TradingAgentsGraph(debug=True, config=config)

        # 运行分析
        _, decision = ta.propagate(ticker, date)

        print()
        print("="*70)
        print("=== 最终交易决策 ===")
        print("="*70)
        print()

        # 使用新的信号处理器显示推荐
        display_trading_recommendation(ticker, decision, save=True)

        print()
        print("[OK] 加密货币分析完成！")
        return True

    except Exception as e:
        print()
        print("="*70)
        print(f"[ERROR] 分析失败: {e}")
        print("="*70)
        print()
        print("详细错误信息:")
        import traceback
        traceback.print_exc()
        print()
        print("可能的原因：")
        print("1. 加密货币代码不正确")
        print("2. CoinGecko API 无法获取该币种数据")
        print("3. 网络连接问题")
        print("4. API 余额不足")
        print()
        print("建议：")
        print("• 检查加密货币代码格式（如：BTC, ETH, SOL）")
        print("• 尝试其他主流加密货币")
        print("• 确认网络连接正常")
        print()

        return False


def main():
    """主函数"""
    print("="*70)
    print("        TradingAgents - 加密货币交易分析系统")
    print("="*70)

    # 显示加密货币代码参考
    show_crypto_reference()

    # 主循环
    while True:
        try:
            # 让用户输入加密货币代码
            ticker = input("请输入加密货币代码（输入 'q' 退出，'h' 查看帮助）: ").strip()

            # 退出命令
            if ticker.lower() == 'q':
                print()
                print("感谢使用 TradingAgents 加密货币版！再见！")
                break

            # 帮助命令
            if ticker.lower() == 'h':
                show_crypto_reference()
                continue

            # 空输入
            if not ticker:
                print("[错误] 加密货币代码不能为空，请重新输入")
                continue

            # 让用户输入日期
            print()
            date_input = input("请输入分析日期（如 2025-01-15，留空使用今天）: ").strip()

            if not date_input:
                from datetime import datetime
                date = datetime.now().strftime("%Y-%m-%d")
                print(f"[INFO] 使用今天日期: {date}")
            else:
                date = date_input

            # 分析加密货币
            success = analyze_crypto(ticker, date)

            # 分析完成提示
            if success:
                print()
                print("="*70)
                print("[完成] 本次分析完成")
                print("="*70)
                print()

            # 询问是否继续
            while True:
                choice = input("是否继续分析其他加密货币？(y/n): ").strip().lower()
                if choice in ['y', 'yes', '是']:
                    print()
                    print("="*70)
                    print("开始新的分析...")
                    print("="*70)
                    break
                elif choice in ['n', 'no', '否']:
                    print()
                    print("感谢使用 TradingAgents 加密货币版！再见！")
                    return
                else:
                    print("请输入 y 或 n")

        except KeyboardInterrupt:
            print()
            print()
            print("检测到 Ctrl+C，正在退出...")
            print("感谢使用 TradingAgents 加密货币版！再见！")
            break
        except Exception as e:
            print()
            print(f"[ERROR] 发生错误: {e}")
            print("请重试或输入 'q' 退出")
            print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 键退出...")
