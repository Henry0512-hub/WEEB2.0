"""
演示版本 - 使用模拟数据展示完整功能
当数据源不可用时使用
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
print("TradingAgents - 数据分析演示系统")
print("=" * 80)
print("\n注意: 本演示使用模拟数据来展示系统功能")
print("      实际使用时将连接WRDS或Yahoo Finance获取真实数据\n")

# ==============================================================================
# 1. 生成模拟数据
# ==============================================================================

def generate_mock_data(ticker="AAPL", days=252):
    """生成模拟股票数据"""
    print(f"[数据] 生成 {ticker} 的模拟数据 ({days} 个交易日)...")

    # 生成日期范围
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='B')

    # 生成价格走势（几何布朗运动）
    np.random.seed(42)  # 固定种子以便复现

    initial_price = 150.0
    returns = np.random.normal(0.0005, 0.02, days)  # 日收益率
    prices = [initial_price]

    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))

    # 创建DataFrame
    data = pd.DataFrame({
        'Close': prices,
        'Volume': np.random.randint(1000000, 50000000, days)
    }, index=dates)

    # 计算收益率
    data['Return'] = data['Close'].pct_change()

    # 添加高开低收
    data['Open'] = data['Close'] * (1 + np.random.uniform(-0.01, 0.01, days))
    data['High'] = data[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, 0.005, days))
    data['Low'] = data[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, 0.005, days))

    print(f"[成功] 生成 {len(data)} 条记录")
    print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")
    print(f"       价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")

    return data

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
    rs = gain / loss.replace(0, np.nan)  # 避免除以0
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

    # RSI信号
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
    print(f"评分: {score}")
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

    # 设置样式
    plt.style.use('seaborn-v0_8-darkgrid')

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # 1. 价格走势
    ax1 = axes[0]
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='#1f77b4')
    ax1.plot(data.index, data['MA_20'], label='MA 20', linewidth=1.5, color='#ff7f0e', alpha=0.7)
    ax1.plot(data.index, data['MA_50'], label='MA 50', linewidth=1.5, color='#2ca02c', alpha=0.7)
    ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.1, color='gray')
    ax1.set_title(f'{ticker} - 价格走势与技术指标', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 ($)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 2. RSI
    ax2 = axes[1]
    ax2.plot(data.index, data['RSI'], label='RSI 14', linewidth=2, color='#d62728')
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
    ax3.hist(returns, bins=50, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax3.axvline(returns.mean(), color='r', linestyle='--', linewidth=2, label=f"均值: {returns.mean():.4f}")
    ax3.axvline(returns.median(), color='g', linestyle='--', linewidth=2, label=f"中位数: {returns.median():.4f}")
    ax3.set_title('收益率分布', fontsize=12, fontweight='bold')
    ax3.set_xlabel('日收益率', fontsize=11)
    ax3.set_ylabel('频数', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # 保存
    chart_path = f"results/{ticker}_analysis.png"
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
{ticker} - 投资分析报告 (演示版本)
{'='*80}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: 模拟数据（用于演示）
分析周期: 1年 ({len(data)} 个交易日)

⚠️  重要提示: 本报告使用模拟数据生成，仅用于演示系统功能。
    实际使用时将连接WRDS或Yahoo Finance获取真实数据。

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

解释:
- 年化收益率: 假设当前收益率持续一年的预期收益
- 年化波动率: 衡量价格波动程度，数值越大风险越高
- 夏普比率: 风险调整后的收益，>1为良好，<0为不佳
- 最大回撤: 历史最大亏损幅度

{'-'*80}
三、技术指标
{'-'*80}

RSI(14): {results['rsi']:.2f}
RSI信号: {results['rsi_signal']}
20日均线: ${data['MA_20'].iloc[-1]:.2f}
50日均线: ${data['MA_50'].iloc[-1]:.2f}

解释:
- RSI > 70: 超买区域，价格可能回调
- RSI < 30: 超卖区域，价格可能反弹
- 价格 > MA20 > MA50: 上升趋势
- 价格 < MA20 < MA50: 下降趋势

{'-'*80}
四、投资建议
{'-'*80}

评级: {results['rating']}
评分: {results['score']}

投资建议说明:
- 强力买入: 多个指标显示强烈买入信号
- 买入: 多数指标显示买入信号
- 持有: 指标混合，建议观望
- 减持: 部分指标显示卖出信号
- 卖出: 多个指标显示卖出信号

{'-'*80}
五、数据分析方法
{'-'*80}

本分析使用的Python技术:
1. 数据获取: pandas, pandas-datareader
2. 数据清洗: 缺失值处理, 异常值检测
3. 技术指标: 移动平均线, RSI, 波动率
4. 统计分析: 收益率, 夏普比率, 最大回撤
5. 可视化: matplotlib, seaborn

{'-'*80}
六、风险提示
{'-'*80}

1. 本报告使用模拟数据，仅供参考
2. 实际投资需要使用真实数据
3. 历史表现不代表未来收益
4. 投资有风险，决策需谨慎
5. 建议结合多种分析方法和专业建议

{'='*80}
报告结束
{'='*80}

附录: Python代码结构
{'='*80}

本系统包含以下模块:
1. 数据获取模块: 支持WRDS、Yahoo Finance、模拟数据
2. 数据清洗模块: 缺失值处理、异常值检测
3. 分析模块: 技术分析、基本面分析、风险评估
4. 可视化模块: 价格图表、技术指标、收益率分布
5. 报告生成模块: 结构化报告、自动生成

生成的文件:
- {ticker}_analysis.png: 分析图表
- {ticker}_report.txt: 文本报告
- {ticker}_data.csv: 原始数据

所有文件保存在: results/ 目录

{'='*80}
"""

    # 保存报告
    report_path = f"results/{ticker}_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[保存] 报告已保存: {report_path}")

    # 打印报告（跳过以避免编码错误）
    try:
        print(report)
    except UnicodeEncodeError:
        print("[提示] 报告包含特殊字符，请查看文件: " + report_path)

    return report_path

# ==============================================================================
# 5. 主程序
# ==============================================================================

def main():
    """主程序"""

    # 分析AAPL
    ticker = "AAPL"

    print("\n[开始] 执行完整分析流程\n")

    # 1. 获取数据（模拟）
    data = generate_mock_data(ticker, days=252)

    # 2. 执行分析
    results, data_with_indicators = analyze_stock(data, ticker)

    # 3. 创建图表
    create_charts(data_with_indicators, ticker, results)

    # 4. 生成报告
    generate_report(ticker, results, data_with_indicators)

    # 5. 保存数据
    data_path = f"results/{ticker}_data.csv"
    data_with_indicators.to_csv(data_path)
    print(f"\n[保存] 数据已保存: {data_path}")

    print(f"\n{'='*80}")
    print("[完成] 分析完成!")
    print(f"{'='*80}")
    print(f"\n已生成文件:")
    print(f"  1. results/{ticker}_analysis.png  - 分析图表 (3个子图)")
    print(f"  2. results/{ticker}_report.txt    - 详细分析报告")
    print(f"  3. results/{ticker}_data.csv      - 原始数据 (含技术指标)")

    print(f"\n{'='*80}")
    print("系统功能演示完成!")
    print(f"{'='*80}")
    print("\n下一步:")
    print("  1. 查看生成的图表和报告")
    print("  2. 连接真实数据源 (WRDS或Yahoo Finance)")
    print("  3. 分析其他股票 (修改ticker参数)")
    print("  4. 扩展分析功能 (添加更多技术指标)")

if __name__ == "__main__":
    try:
        main()
        print("\n程序执行成功! 按Enter键退出...")
        # input()  # 注释掉以便自动运行
    except Exception as e:
        print(f"\n[错误] {str(e)}")
        import traceback
        traceback.print_exc()
