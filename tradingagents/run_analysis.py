"""
TradingAgents - 可直接运行的分析系统
使用WRDS作为主要数据源
"""

import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("TradingAgents - 数据分析系统")
print("=" * 80)
print()

# ==============================================================================
# 1. 数据获取模块
# ==============================================================================

def get_wrds_data(ticker, username, password):
    """使用WRDS获取数据"""
    try:
        import wrds
        print(f"[WRDS] 正在连接...")
        db = wrds.Connection(wrds_username=username, wrds_password=password)
        print(f"[WRDS] 连接成功!")

        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        print(f"[WRDS] 获取 {ticker} 的CRSP数据...")

        # 获取CRSP股票数据
        data = db.get_table(
            library='crsp',
            table='dsf',
            columns=['date', 'prc', 'vol', 'ret', 'bid', 'ask'],
            obs_where=f"ticker='{ticker}'",
            cohort_ops={'date': {'gte': start_date.strftime('%Y-%m-%d'),
                                'lte': end_date.strftime('%Y-%m-%d')}},
            limit=10000
        )

        if not data.empty:
            # 重命名列
            data = data.rename(columns={
                'date': 'Date',
                'prc': 'Close',
                'vol': 'Volume',
                'ret': 'Return'
            })

            # 处理数据
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')
            data = data.sort_index()

            # 处理负价格（Bid/Ask平均）
            data.loc[data['Close'] < 0, 'Close'] = data.loc[data['Close'] < 0, 'bid']

            print(f"[成功] 获取到 {len(data)} 条记录")
            print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")

            return data
        else:
            print(f"[警告] 未找到数据")
            return None

    except ImportError:
        print("[错误] 请先安装WRDS库: pip install wrds")
        return None
    except Exception as e:
        print(f"[错误] WRDS获取失败: {str(e)}")
        return None

def get_yahoo_data(ticker):
    """备用：使用Yahoo Finance获取数据"""
    try:
        import yfinance as yf
        print(f"[Yahoo] 正在获取 {ticker} 的数据...")

        stock = yf.Ticker(ticker)
        data = stock.history(period='1y', progress=False)

        if not data.empty:
            # 重命名列以匹配WRDS格式
            data.index.name = 'Date'
            data = data.rename(columns={'Adj Close': 'Close'})

            # 计算收益率
            data['Return'] = data['Close'].pct_change()

            print(f"[成功] 获取到 {len(data)} 条记录")
            print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")

            return data
        else:
            print(f"[警告] 未找到数据")
            return None

    except Exception as e:
        print(f"[错误] Yahoo获取失败: {str(e)}")
        return None

# ==============================================================================
# 2. 数据分析模块
# ==============================================================================

class StockAnalyzer:
    """股票分析器"""

    def __init__(self, data, ticker):
        self.data = data.copy()
        self.ticker = ticker
        self.results = {}

    def clean_and_prepare(self):
        """数据清洗和准备"""
        print("\n[清洗] 开始数据清洗...")

        # 处理缺失值
        self.data = self.data.fillna(method='ffill').fillna(method='bfill')

        # 计算指标
        self.data['MA_5'] = self.data['Close'].rolling(5).mean()
        self.data['MA_20'] = self.data['Close'].rolling(20).mean()
        self.data['MA_50'] = self.data['Close'].rolling(50).mean()

        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))

        # 波动率
        self.data['Volatility'] = self.data['Return'].rolling(20).std()

        print(f"[完成] 数据清洗完成，新增指标: MA_5, MA_20, MA_50, RSI, Volatility")

    def analyze(self):
        """执行分析"""
        print("\n[分析] 开始分析...")

        # 当前价格
        current_price = self.data['Close'].iloc[-1]
        self.results['current_price'] = current_price

        # 收益率统计
        returns = self.data['Return'].dropna()
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / annual_volatility

        self.results['annual_return'] = annual_return
        self.results['annual_volatility'] = annual_volatility
        self.results['sharpe_ratio'] = sharpe_ratio

        # 最大回撤
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        self.results['max_drawdown'] = max_drawdown

        # 当前RSI
        current_rsi = self.data['RSI'].iloc[-1]
        self.results['rsi'] = current_rsi

        # 趋势判断
        ma_20 = self.data['MA_20'].iloc[-1]
        ma_50 = self.data['MA_50'].iloc[-1]

        if current_price > ma_20 > ma_50:
            trend = "上升趋势"
            trend_score = 2
        elif current_price < ma_20 < ma_50:
            trend = "下降趋势"
            trend_score = -2
        else:
            trend = "震荡"
            trend_score = 0

        self.results['trend'] = trend
        self.results['trend_score'] = trend_score

        # 打印结果
        print(f"[结果] 当前价格: ${current_price:.2f}")
        print(f"[结果] 年化收益率: {annual_return:.2%}")
        print(f"[结果] 年化波动率: {annual_volatility:.2%}")
        print(f"[结果] 夏普比率: {sharpe_ratio:.2f}")
        print(f"[结果] 最大回撤: {max_drawdown:.2%}")
        print(f"[结果] RSI: {current_rsi:.2f}")
        print(f"[结果] 趋势: {trend}")

    def generate_signal(self):
        """生成交易信号"""
        print("\n[信号] 生成交易建议...")

        score = self.results['trend_score']
        signals = []

        # RSI信号
        rsi = self.results['rsi']
        if rsi < 30:
            score += 2
            signals.append(f"RSI超卖 ({rsi:.1f})")
        elif rsi > 70:
            score -= 2
            signals.append(f"RSI超买 ({rsi:.1f})")
        else:
            signals.append(f"RSI中性 ({rsi:.1f})")

        # 夏普比率信号
        sharpe = self.results['sharpe_ratio']
        if sharpe > 1:
            score += 1
            signals.append(f"良好的风险调整收益 (夏普: {sharpe:.2f})")
        elif sharpe < 0:
            score -= 1
            signals.append(f"负风险调整收益 (夏普: {sharpe:.2f})")

        # 生成评级
        if score >= 3:
            rating = "强力买入"
            rating_en = "Strong Buy"
        elif score >= 1:
            rating = "买入"
            rating_en = "Buy"
        elif score >= -1:
            rating = "持有"
            rating_en = "Hold"
        elif score >= -3:
            rating = "减持"
            rating_en = "Underweight"
        else:
            rating = "卖出"
            rating_en = "Sell"

        self.results['rating'] = rating
        self.results['rating_en'] = rating_en
        self.results['score'] = score
        self.results['signals'] = signals

        print(f"[建议] 评级: {rating} ({rating_en})")
        print(f"[建议] 评分: {score}")
        print(f"[建议] 关键信号:")
        for sig in signals:
            print(f"         - {sig}")

# ==============================================================================
# 3. 可视化模块
# ==============================================================================

def create_charts(analyzer, output_dir='results'):
    """创建图表"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n[图表] 生成可视化...")

    ticker = analyzer.ticker
    data = analyzer.data

    # 创建图表
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # 1. 价格走势
    ax1 = axes[0]
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='#2E86AB')
    ax1.plot(data.index, data['MA_20'], label='MA 20', linewidth=1.5, color='#A23B72', alpha=0.7)
    ax1.plot(data.index, data['MA_50'], label='MA 50', linewidth=1.5, color='#F18F01', alpha=0.7)
    ax1.set_title(f'{ticker} - 价格走势与技术指标', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 ($)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 2. RSI
    ax2 = axes[1]
    ax2.plot(data.index, data['RSI'], label='RSI', linewidth=2, color='#C73E1D')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='超买 (70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='超卖 (30)')
    ax2.fill_between(data.index, 30, 70, alpha=0.1, color='gray')
    ax2.set_title('相对强弱指标 (RSI)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('RSI', fontsize=11)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 3. 收益率分布
    ax3 = axes[2]
    returns = data['Return'].dropna()
    ax3.hist(returns, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
    ax3.axvline(returns.mean(), color='r', linestyle='--', linewidth=2, label=f"均值: {returns.mean():.4f}")
    ax3.set_title('收益率分布', fontsize=12, fontweight='bold')
    ax3.set_xlabel('日收益率', fontsize=11)
    ax3.set_ylabel('频数', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # 保存图表
    chart_path = f"{output_dir}/{ticker}_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"[保存] 图表已保存: {chart_path}")

    plt.close()

# ==============================================================================
# 4. 报告生成模块
# ==============================================================================

def generate_report(analyzer, output_dir='results'):
    """生成文本报告"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    ticker = analyzer.ticker
    results = analyzer.results

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"{ticker} - 投资分析报告")
    report_lines.append("=" * 80)
    report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"数据来源: WRDS/CRSP")
    report_lines.append(f"分析周期: 1年")

    report_lines.append("\n" + "-" * 80)
    report_lines.append("一、基本信息")
    report_lines.append("-" * 80)
    report_lines.append(f"\n当前价格: ${results['current_price']:.2f}")
    report_lines.append(f"价格趋势: {results['trend']}")

    report_lines.append("\n" + "-" * 80)
    report_lines.append("二、收益与风险")
    report_lines.append("-" * 80)
    report_lines.append(f"\n年化收益率: {results['annual_return']:.2%}")
    report_lines.append(f"年化波动率: {results['annual_volatility']:.2%}")
    report_lines.append(f"夏普比率: {results['sharpe_ratio']:.2f}")
    report_lines.append(f"最大回撤: {results['max_drawdown']:.2%}")

    report_lines.append("\n" + "-" * 80)
    report_lines.append("三、技术指标")
    report_lines.append("-" * 80)
    report_lines.append(f"\nRSI(14): {results['rsi']:.2f}")
    report_lines.append(f"20日均线: ${analyzer.data['MA_20'].iloc[-1]:.2f}")
    report_lines.append(f"50日均线: ${analyzer.data['MA_50'].iloc[-1]:.2f}")

    report_lines.append("\n" + "-" * 80)
    report_lines.append("四、交易建议")
    report_lines.append("-" * 80)
    report_lines.append(f"\n评级: {results['rating']} ({results['rating_en']})")
    report_lines.append(f"评分: {results['score']}")
    report_lines.append(f"\n关键信号:")
    for sig in results['signals']:
        report_lines.append(f"  • {sig}")

    report_lines.append("\n" + "-" * 80)
    report_lines.append("五、风险提示")
    report_lines.append("-" * 80)
    report_lines.append("\n1. 本报告仅供参考，不构成投资建议")
    report_lines.append("2. 历史表现不代表未来收益")
    report_lines.append("3. 投资有风险，决策需谨慎")

    report_lines.append("\n" + "=" * 80)
    report_lines.append("报告结束")
    report_lines.append("=" * 80)

    report = "\n".join(report_lines)

    # 保存报告
    report_path = f"{output_dir}/{ticker}_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[保存] 报告已保存: {report_path}")

    # 打印报告
    print("\n" + report)

    return report_path

# ==============================================================================
# 5. 主程序
# ==============================================================================

def main():
    """主程序"""

    # WRDS账号
    WRDS_USERNAME = "hengyang24"
    WRDS_PASSWORD = "Appleoppo17@"

    print("\n请输入股票代码 (如 AAPL, TSLA, MSFT):")
    ticker = input("代码: ").strip().upper()

    if not ticker:
        print("[错误] 股票代码不能为空，使用默认AAPL")
        ticker = "AAPL"

    print("\n请选择数据源:")
    print("1. WRDS (推荐，更准确)")
    print("2. Yahoo Finance (备用)")

    choice = input("\n选择 (1 或 2，默认1): ").strip() or "1"

    # 获取数据
    data = None

    if choice == "1":
        print(f"\n[WRDS] 尝试连接WRDS...")
        data = get_wrds_data(ticker, WRDS_USERNAME, WRDS_PASSWORD)

        if data is None or data.empty:
            print(f"[备用] WRDS失败，尝试Yahoo Finance...")
            data = get_yahoo_data(ticker)
    else:
        print(f"\n[Yahoo] 使用Yahoo Finance...")
        data = get_yahoo_data(ticker)

    # 检查数据
    if data is None or data.empty:
        print("\n[错误] 无法获取数据，请检查:")
        print("1. 股票代码是否正确")
        print("2. 网络连接是否正常")
        print("3. WRDS账号是否有效")
        return

    # 执行分析
    print("\n" + "=" * 80)
    print("开始分析")
    print("=" * 80)

    # 创建分析器
    analyzer = StockAnalyzer(data, ticker)

    # 清洗和准备数据
    analyzer.clean_and_prepare()

    # 执行分析
    analyzer.analyze()

    # 生成交易信号
    analyzer.generate_signal()

    # 创建图表
    create_charts(analyzer)

    # 生成报告
    generate_report(analyzer)

    # 保存数据
    data_path = f"results/{ticker}_data.csv"
    data.to_csv(data_path)
    print(f"\n[保存] 数据已保存: {data_path}")

    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)
    print(f"\n已生成文件:")
    print(f"1. results/{ticker}_analysis.png  - 分析图表")
    print(f"2. results/{ticker}_report.txt    - 分析报告")
    print(f"3. results/{ticker}_data.csv      - 原始数据")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
    except Exception as e:
        print(f"\n[错误] 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
