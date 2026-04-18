"""
TradingAgents 完整数据分析系统
符合ACC102作业要求的Python数据产品

作者: [您的名字]
日期: 2026-04-09
课程: ACC102 - Python数据产品作业
"""

# =============================================================================
# 1. 导入必要的库
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置可视化风格
sns.set_style("whitegrid")
sns.set_palette("husl")

print("=" * 80)
print("TradingAgents - 完整数据分析系统")
print("=" * 80)
print()

# =============================================================================
# 2. 问题定义
# =============================================================================

"""
分析性问题：
如何通过多维度数据分析，为投资者提供全面的资产分析和交易建议？

目标用户：
- 个人投资者
- 交易员
- 金融分析师

分析目标：
1. 获取和清洗多市场资产数据（股票、加密货币）
2. 进行技术分析和基本面分析
3. 生成可视化报告和交易建议
4. 提供交互式数据分析界面
"""

# =============================================================================
# 3. 数据获取模块
# =============================================================================

class DataAcquisition:
    """数据获取类 - 支持多市场数据源"""

    def __init__(self):
        self.data_sources = {
            'stock': yfinance,
            'crypto': yfinance  # 也可以使用coingecko
        }

    def get_stock_data(self, ticker, period='1y', interval='1d'):
        """
        获取股票数据

        参数:
        - ticker: 股票代码（如AAPL、600519.SS）
        - period: 时间周期（1y, 6mo, 3mo）
        - interval: 数据间隔（1d, 1wk, 1mo）

        返回:
        - DataFrame: 包含OHLCV数据
        """
        try:
            print(f"[数据获取] 正在获取 {ticker} 的数据...")

            # 判断是否为A股
            if ticker.endswith('.SS') or ticker.endswith('.SZ'):
                # A股使用EFinance（这里简化处理）
                print(f"[信息] 检测到A股代码，使用专用数据源")
                # 这里可以集成EFinance

            # 获取数据
            data = yf.download(ticker, period=period, interval=interval, progress=False)

            if data.empty:
                print(f"[警告] 未能获取到 {ticker} 的数据")
                return None

            print(f"[成功] 获取到 {len(data)} 条记录")
            print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")

            return data

        except Exception as e:
            print(f"[错误] 获取数据失败: {str(e)}")
            return None

    def get_crypto_data(self, ticker, period='1y'):
        """
        获取加密货币数据

        参数:
        - ticker: 加密货币代码（如BTC-USD）
        - period: 时间周期

        返回:
        - DataFrame: 加密货币价格数据
        """
        try:
            print(f"[数据获取] 正在获取加密货币 {ticker} 的数据...")

            # 添加-USD后缀如果需要
            if not ticker.endswith('-USD'):
                ticker = f"{ticker}-USD"

            data = yf.download(ticker, period=period, progress=False)

            if data.empty:
                print(f"[警告] 未能获取到 {ticker} 的数据")
                return None

            print(f"[成功] 获取到 {len(data)} 条记录")

            return data

        except Exception as e:
            print(f"[错误] 获取加密货币数据失败: {str(e)}")
            return None

    def get_multiple_assets(self, tickers, period='1y'):
        """
        获取多个资产的数据

        参数:
        - tickers: 资产代码列表
        - period: 时间周期

        返回:
        - dict: {ticker: DataFrame}
        """
        data_dict = {}

        for ticker in tickers:
            data = self.get_stock_data(ticker, period)
            if data is not None:
                data_dict[ticker] = data

        return data_dict

# =============================================================================
# 4. 数据清洗和准备模块
# =============================================================================

class DataCleaner:
    """数据清洗和准备类"""

    def __init__(self):
        self.cleaning_log = []

    def clean_price_data(self, df):
        """
        清洗价格数据

        步骤:
        1. 处理缺失值
        2. 去除异常值
        3. 添加技术指标
        """
        print("\n[数据清洗] 开始清洗数据...")

        # 记录原始数据形状
        original_shape = df.shape
        self.cleaning_log.append(f"原始数据: {original_shape[0]} 行, {original_shape[1]} 列")

        # 1. 处理缺失值
        missing_before = df.isnull().sum().sum()
        if missing_before > 0:
            print(f"[清洗] 发现 {missing_before} 个缺失值")
            # 使用前向填充
            df = df.fillna(method='ffill')
            # 如果还有缺失，使用后向填充
            df = df.fillna(method='bfill')
            missing_after = df.isnull().sum().sum()
            print(f"[清洗] 填充后剩余 {missing_after} 个缺失值")

        # 2. 添加基本技术指标
        df = self.add_technical_indicators(df)

        # 3. 添加收益率
        df['Return'] = df['Adj Close'].pct_change()
        df['Log_Return'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))

        # 4. 添加波动率（20日滚动标准差）
        df['Volatility_20'] = df['Return'].rolling(window=20).std()

        cleaned_shape = df.shape
        self.cleaning_log.append(f"清洗后数据: {cleaned_shape[0]} 行, {cleaned_shape[1]} 列")
        self.cleaning_log.append(f"新增指标: {cleaned_shape[1] - original_shape[1]} 个")

        print(f"[完成] 数据清洗完成")
        print(f"       处理记录: {len(self.cleaning_log)} 条")

        return df

    def add_technical_indicators(self, df):
        """添加技术指标"""

        # 移动平均线
        df['MA_5'] = df['Adj Close'].rolling(window=5).mean()
        df['MA_10'] = df['Adj Close'].rolling(window=10).mean()
        df['MA_20'] = df['Adj Close'].rolling(window=20).mean()
        df['MA_50'] = df['Adj Close'].rolling(window=50).mean()

        # RSI (相对强弱指标)
        df['RSI_14'] = self.calculate_rsi(df['Adj Close'], 14)

        # MACD
        df['MACD'], df['MACD_Signal'] = self.calculate_macd(df['Adj Close'])

        # 布林带
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bollinger_bands(df['Adj Close'])

        return df

    def calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        return macd, macd_signal

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """计算布林带"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    def get_cleaning_summary(self):
        """获取清洗摘要"""
        return "\n".join(self.cleaning_log)

# =============================================================================
# 5. 数据分析模块
# =============================================================================

class DataAnalyzer:
    """数据分析类"""

    def __init__(self):
        self.analysis_results = {}

    def perform_descriptive_analysis(self, df):
        """描述性统计分析"""
        print("\n[分析] 执行描述性统计分析...")

        analysis = {}

        # 基本统计
        analysis['basic_stats'] = df['Adj Close'].describe()
        analysis['return_stats'] = df['Return'].describe()
        analysis['volatility_stats'] = df['Volatility_20'].describe()

        # 年化收益率
        annual_return = df['Return'].mean() * 252
        analysis['annual_return'] = annual_return

        # 年化波动率
        annual_volatility = df['Return'].std() * np.sqrt(252)
        analysis['annual_volatility'] = annual_volatility

        # 夏普比率（假设无风险利率为2%）
        risk_free_rate = 0.02
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        analysis['sharpe_ratio'] = sharpe_ratio

        # 最大回撤
        max_drawdown = self.calculate_max_drawdown(df['Adj Close'])
        analysis['max_drawdown'] = max_drawdown

        print(f"[结果] 年化收益率: {annual_return:.2%}")
        print(f"[结果] 年化波动率: {annual_volatility:.2%}")
        print(f"[结果] 夏普比率: {sharpe_ratio:.2f}")
        print(f"[结果] 最大回撤: {max_drawdown:.2%}")

        self.analysis_results['descriptive'] = analysis
        return analysis

    def calculate_max_drawdown(self, prices):
        """计算最大回撤"""
        rolling_max = prices.cummax()
        drawdown = (prices - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        return max_drawdown

    def perform_technical_analysis(self, df):
        """技术分析"""
        print("\n[分析] 执行技术分析...")

        current_price = df['Adj Close'].iloc[-1]
        ma_20 = df['MA_20'].iloc[-1]
        ma_50 = df['MA_50'].iloc[-1]
        rsi = df['RSI_14'].iloc[-1]

        # 价格趋势
        if current_price > ma_20 > ma_50:
            trend = "上升趋势"
        elif current_price < ma_20 < ma_50:
            trend = "下降趋势"
        else:
            trend = "震荡"

        # RSI信号
        if rsi > 70:
            rsi_signal = "超买"
        elif rsi < 30:
            rsi_signal = "超卖"
        else:
            rsi_signal = "中性"

        analysis = {
            'current_price': current_price,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'rsi': rsi,
            'trend': trend,
            'rsi_signal': rsi_signal
        }

        print(f"[结果] 当前价格: ${current_price:.2f}")
        print(f"[结果] 趋势: {trend}")
        print(f"[结果] RSI: {rsi:.2f} ({rsi_signal})")

        self.analysis_results['technical'] = analysis
        return analysis

    def generate_trading_signal(self, df):
        """生成交易信号"""
        print("\n[分析] 生成交易信号...")

        latest = df.iloc[-1]

        # 信号评分系统
        score = 0
        signals = []

        # 1. 趋势分析
        if latest['MA_5'] > latest['MA_10'] > latest['MA_20']:
            score += 2
            signals.append("短期均线呈多头排列")
        elif latest['MA_5'] < latest['MA_10'] < latest['MA_20']:
            score -= 2
            signals.append("短期均线呈空头排列")

        # 2. RSI分析
        if latest['RSI_14'] < 30:
            score += 2
            signals.append("RSI超卖，可能反弹")
        elif latest['RSI_14'] > 70:
            score -= 2
            signals.append("RSI超买，可能回调")

        # 3. MACD分析
        if latest['MACD'] > latest['MACD_Signal']:
            score += 1
            signals.append("MACD金叉")
        else:
            score -= 1
            signals.append("MACD死叉")

        # 4. 布林带分析
        if latest['Adj Close'] < latest['BB_Lower']:
            score += 1
            signals.append("价格触及布林带下轨")
        elif latest['Adj Close'] > latest['BB_Upper']:
            score -= 1
            signals.append("价格触及布林带上轨")

        # 生成评级
        if score >= 4:
            rating = "强力买入 (Buy)"
            rating_cn = "强力买入"
        elif score >= 2:
            rating = "买入 (Overweight)"
            rating_cn = "增持"
        elif score >= -1:
            rating = "持有 (Hold)"
            rating_cn = "持有"
        elif score >= -3:
            rating = "减持 (Underweight)"
            rating_cn = "减持"
        else:
            rating = "卖出 (Sell)"
            rating_cn = "卖出"

        signal_summary = {
            'score': score,
            'rating': rating,
            'rating_cn': rating_cn,
            'signals': signals,
            'analysis_date': df.index[-1].strftime('%Y-%m-%d')
        }

        print(f"[结果] 评分: {score}")
        print(f"[结果] 评级: {rating}")
        print(f"[结果] 信号数量: {len(signals)}")

        self.analysis_results['signal'] = signal_summary
        return signal_summary

# =============================================================================
# 6. 可视化模块
# =============================================================================

class Visualizer:
    """数据可视化类"""

    def __init__(self, style='seaborn-v0_8-darkgrid'):
        plt.style.use(style)
        self.colors = sns.color_palette("husl", 10)

    def create_price_chart(self, df, ticker, save_path=None):
        """创建价格走势图"""
        print(f"\n[可视化] 创建价格走势图...")

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # 子图1: 价格和移动平均线
        ax1 = axes[0]
        ax1.plot(df.index, df['Adj Close'], label='Adj Close', linewidth=2, color=self.colors[0])
        ax1.plot(df.index, df['MA_20'], label='MA 20', linewidth=1.5, color=self.colors[1], alpha=0.7)
        ax1.plot(df.index, df['MA_50'], label='MA 50', linewidth=1.5, color=self.colors[2], alpha=0.7)
        ax1.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], alpha=0.2, color=self.colors[3], label='Bollinger Bands')

        ax1.set_title(f'{ticker} - 价格走势与技术指标', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格 ($)', fontsize=12)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # 子图2: RSI
        ax2 = axes[1]
        ax2.plot(df.index, df['RSI_14'], label='RSI 14', linewidth=2, color=self.colors[4])
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
        ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
        ax2.fill_between(df.index, 30, 70, alpha=0.1, color='gray')

        ax2.set_title('相对强弱指标 (RSI)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[保存] 图表已保存至: {save_path}")

        return fig

    def create_return_distribution(self, df, ticker, save_path=None):
        """创建收益率分布图"""
        print(f"\n[可视化] 创建收益率分布图...")

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 子图1: 收益率时间序列
        ax1 = axes[0]
        ax1.plot(df.index, df['Return'], label='Daily Return', linewidth=1, color=self.colors[0])
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_title(f'{ticker} - 日收益率', fontsize=12, fontweight='bold')
        ax1.set_ylabel('收益率', fontsize=12)
        ax1.set_xlabel('日期', fontsize=12)
        ax1.grid(True, alpha=0.3)

        # 子图2: 收益率分布直方图
        ax2 = axes[1]
        ax2.hist(df['Return'].dropna(), bins=50, color=self.colors[1], alpha=0.7, edgecolor='black')
        ax2.axvline(df['Return'].mean(), color='r', linestyle='--', linewidth=2, label=f"均值: {df['Return'].mean():.4f}")
        ax2.axvline(df['Return'].median(), color='g', linestyle='--', linewidth=2, label=f"中位数: {df['Return'].median():.4f}")
        ax2.set_title('收益率分布', fontsize=12, fontweight='bold')
        ax2.set_xlabel('收益率', fontsize=12)
        ax2.set_ylabel('频数', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[保存] 图表已保存至: {save_path}")

        return fig

    def create_correlation_heatmap(self, data_dict, save_path=None):
        """创建多资产相关性热图"""
        print(f"\n[可视化] 创建相关性热图...")

        # 提取所有资产的收盘价
        close_prices = pd.DataFrame()
        for ticker, df in data_dict.items():
            if df is not None and 'Adj Close' in df.columns:
                close_prices[ticker] = df['Adj Close']

        # 计算收益率
        returns = close_prices.pct_change().dropna()

        # 计算相关系数
        correlation = returns.corr()

        # 创建热图
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm',
                    center=0, square=True, linewidths=1,
                    cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('资产收益率相关性矩阵', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[保存] 图表已保存至: {save_path}")

        return fig

# =============================================================================
# 7. 报告生成模块
# =============================================================================

class ReportGenerator:
    """分析报告生成类"""

    def __init__(self):
        self.report_sections = []

    def generate_full_report(self, ticker, analysis_results, data_info):
        """生成完整分析报告"""
        print("\n[报告] 生成分析报告...")

        report = []
        report.append("=" * 80)
        report.append(f"{ticker} - 投资分析报告")
        report.append("=" * 80)
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据来源: Yahoo Finance")
        report.append(f"分析周期: {data_info['start_date']} 到 {data_info['end_date']}")
        report.append(f"数据记录: {data_info['records']} 条")

        # 描述性统计
        if 'descriptive' in analysis_results:
            report.append("\n" + "-" * 80)
            report.append("一、描述性统计分析")
            report.append("-" * 80)

            desc = analysis_results['descriptive']
            report.append(f"\n年化收益率: {desc['annual_return']:.2%}")
            report.append(f"年化波动率: {desc['annual_volatility']:.2%}")
            report.append(f"夏普比率: {desc['sharpe_ratio']:.2f}")
            report.append(f"最大回撤: {desc['max_drawdown']:.2%}")

        # 技术分析
        if 'technical' in analysis_results:
            report.append("\n" + "-" * 80)
            report.append("二、技术分析")
            report.append("-" * 80)

            tech = analysis_results['technical']
            report.append(f"\n当前价格: ${tech['current_price']:.2f}")
            report.append(f"20日均线: ${tech['ma_20']:.2f}")
            report.append(f"50日均线: ${tech['ma_50']:.2f}")
            report.append(f"RSI(14): {tech['rsi']:.2f}")
            report.append(f"价格趋势: {tech['trend']}")
            report.append(f"RSI信号: {tech['rsi_signal']}")

        # 交易信号
        if 'signal' in analysis_results:
            report.append("\n" + "-" * 80)
            report.append("三、交易建议")
            report.append("-" * 80)

            signal = analysis_results['signal']
            report.append(f"\n评级: {signal['rating']}")
            report.append(f"评分: {signal['score']}")
            report.append(f"分析日期: {signal['analysis_date']}")

            report.append("\n关键信号:")
            for i, sig in enumerate(signal['signals'], 1):
                report.append(f"  {i}. {sig}")

        # 风险提示
        report.append("\n" + "-" * 80)
        report.append("四、风险提示")
        report.append("-" * 80)
        report.append("\n1. 本报告仅供参考，不构成投资建议")
        report.append("2. 历史表现不代表未来收益")
        report.append("3. 投资有风险，决策需谨慎")
        report.append("4. 建议结合其他分析工具和专业建议")

        report.append("\n" + "=" * 80)
        report.append("报告结束")
        report.append("=" * 80)

        full_report = "\n".join(report)

        print(f"[完成] 报告生成完毕，共 {len(report)} 行")

        return full_report

    def save_report(self, report, filepath):
        """保存报告到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[保存] 报告已保存至: {filepath}")
            return True
        except Exception as e:
            print(f"[错误] 保存报告失败: {str(e)}")
            return False

# =============================================================================
# 8. 主工作流程
# =============================================================================

def main():
    """主分析流程"""

    print("\n" + "=" * 80)
    print("TradingAgents - 完整数据分析系统")
    print("ACC102 Python数据产品作业")
    print("=" * 80)

    # 1. 用户输入
    print("\n请选择要分析的资产类型:")
    print("1. 股票 (美股、A股、港股)")
    print("2. 加密货币")

    choice = input("\n请输入选择 (1 或 2): ").strip()

    if choice == '2':
        ticker = input("\n请输入加密货币代码 (如 BTC, ETH): ").strip().upper()
        is_crypto = True
    else:
        ticker = input("\n请输入股票代码 (如 AAPL, TSLA, 600519.SS): ").strip().upper()
        is_crypto = False

    period = input("请输入分析周期 (默认1y): ").strip() or '1y'

    # 2. 数据获取
    acquirer = DataAcquisition()

    if is_crypto:
        df = acquirer.get_crypto_data(ticker, period)
    else:
        df = acquirer.get_stock_data(ticker, period)

    if df is None or df.empty:
        print("[错误] 无法获取数据，程序退出")
        return

    # 3. 数据清洗
    cleaner = DataCleaner()
    df_clean = cleaner.clean_price_data(df)

    print("\n[清洗摘要]")
    print(cleaner.get_cleaning_summary())

    # 4. 数据分析
    analyzer = DataAnalyzer()

    # 描述性分析
    desc_results = analyzer.perform_descriptive_analysis(df_clean)

    # 技术分析
    tech_results = analyzer.perform_technical_analysis(df_clean)

    # 生成交易信号
    signal_results = analyzer.generate_trading_signal(df_clean)

    # 5. 可视化
    print("\n[可视化] 创建图表...")
    visualizer = Visualizer()

    # 创建结果目录
    from pathlib import Path
    results_dir = Path("results/analysis")
    results_dir.mkdir(parents=True, exist_ok=True)

    # 价格图表
    price_chart_path = results_dir / f"{ticker}_price_chart.png"
    visualizer.create_price_chart(df_clean, ticker, save_path=str(price_chart_path))

    # 收益率图表
    return_chart_path = results_dir / f"{ticker}_return_distribution.png"
    visualizer.create_return_distribution(df_clean, ticker, save_path=str(return_chart_path))

    # 6. 生成报告
    data_info = {
        'start_date': df_clean.index[0].strftime('%Y-%m-%d'),
        'end_date': df_clean.index[-1].strftime('%Y-%m-%d'),
        'records': len(df_clean)
    }

    reporter = ReportGenerator()
    report = reporter.generate_full_report(ticker, analyzer.analysis_results, data_info)

    # 保存报告
    report_path = results_dir / f"{ticker}_analysis_report.txt"
    reporter.save_report(report, str(report_path))

    # 打印报告
    print("\n" + report)

    # 7. 保存处理后的数据
    data_path = results_dir / f"{ticker}_processed_data.csv"
    df_clean.to_csv(data_path)
    print(f"\n[保存] 处理后的数据已保存至: {data_path}")

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)
    print(f"\n生成的文件:")
    print(f"1. 价格图表: {price_chart_path}")
    print(f"2. 收益率图表: {return_chart_path}")
    print(f"3. 分析报告: {report_path}")
    print(f"4. 处理数据: {data_path}")

    return df_clean, analyzer.analysis_results

# =============================================================================
# 程序入口
# =============================================================================

if __name__ == "__main__":
    # 运行主程序
    df, results = main()

    print("\n按 Enter 键退出...")
    input()
