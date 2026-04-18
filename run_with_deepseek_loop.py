"""
使用 DeepSeek API 运行 TradingAgents 的交互式脚本（循环版本）

配置说明：
1. DeepSeek API 已配置
2. 模型使用 deepseek-chat
3. 自动检测股票类型并选择最佳数据源

使用方法：
python run_with_deepseek_loop.py
"""

import os
import sys
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.smart_router import get_smart_config

# 加载环境变量
load_dotenv()

# 从配置文件加载API密钥
try:
    from api_config import DEEPSEEK_API_KEY
    os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY
except ImportError:
    DEEPSEEK_API_KEY = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"
    os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY


def show_stock_reference():
    """显示常用资产代码参考（股票 + 加密货币）"""
    print()
    print("="*70)
    print("常用资产代码参考：")
    print("="*70)
    print()
    print("₿ 加密货币（新支持！）：")
    print("  BTC    - 比特币 (Bitcoin)")
    print("  ETH    - 以太坊 (Ethereum)")
    print("  BNB    - 币安币 (Binance Coin)")
    print("  SOL    - Solana")
    print("  XRP    - 瑞波币 (XRP)")
    print("  ADA    - 艾达币 (Cardano)")
    print("  DOGE   - 狗狗币 (Dogecoin)")
    print("  DOT    - 波卡 (Polkadot)")
    print("  MATIC  - Polygon")
    print("  AVAX   - Avalanche")
    print("  LINK   - Chainlink")
    print("  UNI    - Uniswap")
    print()
    print("🇺🇸 美股科技股：")
    print("  AAPL   - 苹果")
    print("  TSLA   - 特斯拉")
    print("  NVDA   - 英伟达")
    print("  MSFT   - 微软")
    print("  GOOGL  - 谷歌")
    print()
    print("🇨🇳 中概股：")
    print("  BABA   - 阿里巴巴")
    print("  JD     - 京东")
    print("  BIDU   - 百度")
    print("  PDD    - 拼多多")
    print("  NTES   - 网易")
    print()
    print("🇭🇰 港股：")
    print("  0700.HK  - 腾讯控股")
    print("  9988.HK  - 阿里巴巴港股")
    print()
    print("🇨🇳 A股（新支持！）：")
    print("  600519.SS - 贵州茅台")
    print("  000001.SZ - 平安银行")
    print("  600036.SS - 招商银行")
    print("  002594.SZ - 比亚迪")
    print()
    print("="*70)
    print()


def analyze_stock(ticker, date):
    """
    分析单只股票

    Args:
        ticker: 股票代码
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

    # 数据源配置
    config["data_vendors"] = {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    }

    # 智能数据源路由 - 自动检测A股并使用efinance
    config = get_smart_config(ticker, config)

    print("[INFO] 初始化 TradingAgents（使用 DeepSeek）...")
    print("[INFO] 多智能体分析系统启动中...")
    print()

    # 显示智能体列表
    print("智能体团队：")
    print("  ✓ 基本面分析师 - 分析公司财务")
    print("  ✓ 情绪分析师 - 分析市场情绪")
    print("  ✓ 新闻分析师 - 分析相关新闻")
    print("  ✓ 技术分析师 - 分析技术指标")
    print("  ✓ 研究员团队 - 辩论分析")
    print("  ✓ 交易员 - 制定交易策略")
    print("  ✓ 风险管理团队 - 评估风险")
    print("  ✓ 投资组合经理 - 最终决策")
    print()
    print("请稍候，这可能需要几分钟...")
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
        print(decision)
        print()
        print("="*70)
        print()

        print("[OK] 分析完成！")
        return True

    except Exception as e:
        print()
        print("="*70)
        print(f"[ERROR] 分析失败: {e}")
        print("="*70)
        print()
        print("可能的原因：")
        print("1. 股票代码不正确（注意区分大小写）")
        print("2. 数据源无法获取该股票数据")
        print("3. 网络连接问题")
        print("4. API 余额不足")
        print()
        print("建议：")
        print("• 检查股票代码格式")
        print("• 尝试其他股票代码")
        print("• 确认网络连接正常")
        print()

        return False


def main():
    """主函数"""
    print("="*70)
    print("           TradingAgents - 交互式股票分析（循环模式）")
    print("="*70)

    # 显示股票代码参考
    show_stock_reference()

    # 主循环
    while True:
        try:
            # 让用户输入股票代码
            ticker = input("请输入股票代码（输入 'q' 退出，'h' 查看帮助）: ").strip()

            # 退出命令
            if ticker.lower() == 'q':
                print()
                print("感谢使用 TradingAgents！再见！")
                break

            # 帮助命令
            if ticker.lower() == 'h':
                show_stock_reference()
                continue

            # 空输入
            if not ticker:
                print("[错误] 股票代码不能为空，请重新输入")
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

            # 分析股票
            success = analyze_stock(ticker, date)

            # 分析完成提示
            if success:
                print()
                print("="*70)
                print("✓ 本次分析完成")
                print("="*70)
                print()

            # 询问是否继续
            while True:
                choice = input("是否继续分析其他股票？(y/n): ").strip().lower()
                if choice in ['y', 'yes', '是']:
                    print()
                    print("="*70)
                    print("开始新的分析...")
                    print("="*70)
                    break
                elif choice in ['n', 'no', '否']:
                    print()
                    print("感谢使用 TradingAgents！再见！")
                    return
                else:
                    print("请输入 y 或 n")

        except KeyboardInterrupt:
            print()
            print()
            print("检测到 Ctrl+C，正在退出...")
            print("感谢使用 TradingAgents！再见！")
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
