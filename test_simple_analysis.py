"""
使用pandas-datareader的简化版本
不依赖WRDS交互式输入
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TradingAgents - 简化分析系统")
print("=" * 80)

# ==============================================================================
# 1. 数据获取（使用pandas-datareader）
# ==============================================================================

def get_stock_data(ticker, source='yahoo'):
    """获取股票数据"""
    try:
        import pandas_datareader.data as web
        print(f"[数据] 从{source}获取 {ticker} 的数据...")

        # 计算1年时间范围
        end = datetime.now()
        start = end - timedelta(days=365)

        # 获取数据
        data = web.DataReader(
            ticker,
            source,
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d')
        )

        if not data.empty:
            # 确保有Adj Close
            if 'Adj Close' in data.columns:
                data['Close'] = data['Adj Close']

            # 计算收益率
            data['Return'] = data['Close'].pct_change()

            print(f"[成功] 获取到 {len(data)} 条记录")
            print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")
            print(f"       价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")

            return data
        else:
            print(f"[警告] 未找到数据")
            return None

    except ImportError:
        print("[错误] 请安装pandas-datareader: pip install pandas-datareader")
        return None
    except Exception as e:
        print(f"[错误] 获取数据失败: {str(e)}")
        return None

# ==============================================================================
# 2. 数据分析
# ==============================================================================

def analyze_stock(data, ticker):
    """分析股票数据"""
    print(f"\n[分析] 开始分析 {ticker}...")

    results = {}

    # 基本统计
    current_price = data['Close'].iloc[-1]
    results['current_price'] = current_price

    # 计算技术指标
    data['MA_5'] = data['Close'].rolling(5).mean()
    data['MA_20'] = data['Close'].rolling(20).mean()
    data['MA_50'] = data['Close'].rolling(50).mean()

    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # 收益率统计
    returns = data['Return'].dropna()
    annual_return = returns.mean() * 252
    annual_volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (annual_return - 0.02) / annual_volatility

    results['annual_return'] = annual_return
    results['annual_volatility'] = annual_volatility
    results['sharpe_ratio'] = sharpe_ratio

    # 最大回撤
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    results['max_drawdown'] = max_drawdown

    # 当前RSI
    current_rsi = data['RSI'].iloc[-1]
    results['rsi'] = current_rsi

    # 趋势
    ma_20 = data['MA_20'].iloc[-1]
    ma_50 = data['MA_50'].iloc[-1]

    if current_price > ma_20 > ma_50:
        trend = "上升趋势"
        score = 2
    elif current_price < ma_20 < ma_50:
        trend = "下降趋势"
        score = -2
    else:
        trend = "震荡"
        score = 0

    results['trend'] = trend
    results['score'] = score

    # RSI评分
    if current_rsi < 30:
        score += 2
        rsi_signal = "超卖"
    elif current_rsi > 70:
        score -= 2
        rsi_signal = "超买"
    else:
        rsi_signal = "中性"

    results['rsi_signal'] = rsi_signal

    # 生成评级
    if score >= 3:
        rating = "强力买入"
    elif score >= 1:
        rating = "买入"
    elif score >= -1:
        rating = "持有"
    elif score >= -3:
        rating = "减持"
    else:
        rating = "卖出"

    results['rating'] = rating

    # 打印结果
    print(f"\n{'='*60}")
    print(f"分析结果: {ticker}")
    print(f"{'='*60}")
    print(f"当前价格: ${current_price:.2f}")
    print(f"价格趋势: {trend}")
    print(f"年化收益: {annual_return:.2%}")
    print(f"年化波动: {annual_volatility:.2%}")
    print(f"夏普比率: {sharpe_ratio:.2f}")
    print(f"最大回撤: {max_drawdown:.2%}")
    print(f"RSI(14): {current_rsi:.2f} ({rsi_signal})")
    print(f"\n投资建议: {rating}")
    print(f"{'='*60}")

    return results, data

# ==============================================================================
# 3. 创建图表
# ==============================================================================

def create_charts(data, ticker, results):
    """创建分析图表"""
    import os
    os.makedirs('results', exist_ok=True)

    print(f"\n[图表] 生成可视化...")

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # 价格走势
    ax1 = axes[0]
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='#1f77b4')
    ax1.plot(data.index, data['MA_20'], label='MA 20', linewidth=1.5, color='#ff7f0e', alpha=0.7)
    ax1.plot(data.index, data['MA_50'], label='MA 50', linewidth=1.5, color='#2ca02c', alpha=0.7)
    ax1.set_title(f'{ticker} - 价格走势分析', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 ($)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # RSI
    ax2 = axes[1]
    ax2.plot(data.index, data['RSI'], label='RSI 14', linewidth=2, color='#d62728')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='超买 (70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='超卖 (30)')
    ax2.fill_between(data.index, 30, 70, alpha=0.1, color='gray')
    ax2.set_title('相对强弱指标 (RSI)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('RSI', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存
    chart_path = f"results/{ticker}_charts.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"[保存] 图表已保存: {chart_path}")

    plt.close()

# ==============================================================================
# 4. 生成报告
# ==============================================================================

def generate_report(ticker, results, data):
    """生成文本报告"""
    import os
    os.makedirs('results', exist_ok=True)

    report = f"""
{'='*80}
{ticker} - 投资分析报告
{'='*80}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: pandas-datareader (Yahoo Finance)
分析周期: 1年

{'-'*80}
一、基本信息
{'-'*80}

股票代码: {ticker}
当前价格: ${results['current_price']:.2f}
价格趋势: {results['trend']}

{'-'*80}
二、收益与风险分析
{'-'*80}

年化收益率: {results['annual_return']:.2%}
年化波动率: {results['annual_volatility']:.2%}
夏普比率: {results['sharpe_ratio']:.2f}
最大回撤: {results['max_drawdown']:.2%}

{'-'*80}
三、技术指标
{'-'*80}

RSI(14): {results['rsi']:.2f}
RSI信号: {results['rsi_signal']}
20日均线: ${data['MA_20'].iloc[-1]:.2f}
50日均线: ${data['MA_50'].iloc[-1]:.2f}

{'-'*80}
四、投资建议
{'-'*80}

评级: {results['rating']}
评分: {results['score']}

{'-'*80}
五、风险提示
{'-'*80}

1. 本报告仅供参考，不构成投资建议
2. 历史表现不代表未来收益
3. 投资有风险，决策需谨慎
4. 建议结合多种分析方法

{'='*80}
报告结束
{'='*80}
"""

    # 保存报告
    report_path = f"results/{ticker}_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[保存] 报告已保存: {report_path}")

    # 打印报告
    print(report)

    return report_path

# ==============================================================================
# 5. 主程序
# ==============================================================================

def main():
    """主程序"""

    # 默认分析AAPL
    ticker = "AAPL"

    # 获取数据
    data = get_stock_data(ticker)

    if data is None or data.empty:
        print("\n[错误] 无法获取数据")
        return

    # 执行分析
    results, data_with_indicators = analyze_stock(data, ticker)

    # 创建图表
    create_charts(data_with_indicators, ticker, results)

    # 生成报告
    generate_report(ticker, results, data_with_indicators)

    # 保存数据
    data_path = f"results/{ticker}_data.csv"
    data_with_indicators.to_csv(data_path)
    print(f"\n[保存] 数据已保存: {data_path}")

    print(f"\n{'='*80}")
    print("分析完成!")
    print(f"{'='*80}")
    print(f"\n已生成文件:")
    print(f"1. results/{ticker}_charts.png  - 分析图表")
    print(f"2. results/{ticker}_report.txt   - 分析报告")
    print(f"3. results/{ticker}_data.csv     - 原始数据")

if __name__ == "__main__":
    try:
        main()
        print("\n程序执行成功!")
    except Exception as e:
        print(f"\n[错误] {str(e)}")
        import traceback
        traceback.print_exc()
