"""
TradingAgents 简化版 - 使用WRDS数据分析系统
可以直接运行的版本
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ==============================================================================
# WRDS 连接模块
# ==============================================================================

class WRDSConnector:
    """WRDS数据库连接类"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.db = None

    def connect(self):
        """连接到WRDS数据库"""
        try:
            import wrds
            print("[WRDS] 正在连接到WRDS数据库...")
            self.db = wrds.Connection(wrds_username=self.username, wrds_password=self.password)
            print("[成功] WRDS连接成功!")
            return True
        except Exception as e:
            print(f"[错误] WRDS连接失败: {str(e)}")
            print("[提示] 请安装WRDS库: pip install wrds")
            return False

    def get_stock_data(self, ticker, start_date, end_date):
        """从WRDS获取股票数据（CRSP）"""
        try:
            print(f"[WRDS] 获取 {ticker} 的数据...")

            # 使用CRSP获取股票数据
            data = self.db.get_table(
                library='crsp',
                table='dsf',
                columns=['date', 'prc', 'bid', 'ask', 'vol', 'ret'],
                obs_where=f"ticker='{ticker}'",
                cohort_ops={'date': {'gte': start_date, 'lte': end_date}},
                limit=10000
            )

            if not data.empty:
                data = data.rename(columns={
                    'date': 'Date',
                    'prc': 'Close',
                    'vol': 'Volume',
                    'ret': 'Return'
                })
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
                data = data.sort_index()

                print(f"[成功] 获取到 {len(data)} 条记录")
                return data
            else:
                print(f"[警告] 未找到 {ticker} 的数据")
                return None

        except Exception as e:
            print(f"[错误] 获取WRDS数据失败: {str(e)}")
            return None

    def get_compustat_data(self, ticker, start_date, end_date):
        """从WRDS获取基本面数据（Compustat）"""
        try:
            print(f"[WRDS] 获取 {ticker} 的基本面数据...")

            # 使用Compustat获取财务数据
            data = self.db.get_table(
                library='comp',
                table='funda',
                columns=['datadate', 'tic', 'sale', 'ni', 'at', 'lt'],
                obs_where=f"tic='{ticker}'",
                cohort_ops={'datadate': {'gte': start_date, 'lte': end_date}},
                limit=1000
            )

            if not data.empty:
                print(f"[成功] 获取到 {len(data)} 条基本面记录")
                return data
            else:
                print(f"[警告] 未找到 {ticker} 的基本面数据")
                return None

        except Exception as e:
            print(f"[错误] 获取Compustat数据失败: {str(e)}")
            return None

# ==============================================================================
# 备用数据源（使用yfinance，不需要WRDS）
# ==============================================================================

class YahooDataSource:
    """Yahoo Finance 数据源类"""

    def __init__(self):
        pass

    def get_stock_data(self, ticker, period='1y'):
        """从Yahoo Finance获取股票数据"""
        try:
            import yfinance as yf
            print(f"[Yahoo] 正在获取 {ticker} 的数据...")

            stock = yf.Ticker(ticker)
            data = stock.history(period=period)

            if not data.empty:
                print(f"[成功] 获取到 {len(data)} 条记录")
                print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")
                return data
            else:
                print(f"[警告] 未找到 {ticker} 的数据")
                return None

        except Exception as e:
            print(f"[错误] 获取Yahoo数据失败: {str(e)}")
            return None

# ==============================================================================
# 数据分析类
# ==============================================================================

class StockAnalyzer:
    """股票分析类"""

    def __init__(self, data):
        self.data = data.copy()
        self.analysis_results = {}

    def clean_data(self):
        """数据清洗"""
        print("\n[清洗] 开始清洗数据...")

        # 处理缺失值
        missing_before = self.data.isnull().sum().sum()
        print(f"[清洗] 发现 {missing_before} 个缺失值")

        self.data = self.data.fillna(method='ffill').fillna(method='bfill')

        # 计算收益率
        if 'Close' in self.data.columns:
            self.data['Return'] = self.data['Close'].pct_change()
            self.data['Log_Return'] = np.log(self.data['Close'] / self.data['Close'].shift(1))

        # 计算移动平均线
        if 'Close' in self.data.columns:
            self.data['MA_5'] = self.data['Close'].rolling(window=5).mean()
            self.data['MA_20'] = self.data['Close'].rolling(window=20).mean()
            self.data['MA_50'] = self.data['Close'].rolling(window=50).mean()

        # 计算RSI
        if 'Close' in self.data.columns:
            self.data['RSI_14'] = self.calculate_rsi(self.data['Close'], 14)

        print(f"[完成] 数据清洗完成")

    def calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def perform_analysis(self):
        """执行分析"""
        print("\n[分析] 开始执行分析...")

        # 基本统计
        if 'Close' in self.data.columns:
            current_price = self.data['Close'].iloc[-1]
            self.analysis_results['current_price'] = current_price

            # 收益率统计
            if 'Return' in self.data.columns:
                annual_return = self.data['Return'].mean() * 252
                annual_volatility = self.data['Return'].std() * np.sqrt(252)
                sharpe_ratio = (annual_return - 0.02) / annual_volatility

                self.analysis_results['annual_return'] = annual_return
                self.analysis_results['annual_volatility'] = annual_volatility
                self.analysis_results['sharpe_ratio'] = sharpe_ratio

                print(f"[分析] 年化收益率: {annual_return:.2%}")
                print(f"[分析] 年化波动率: {annual_volatility:.2%}")
                print(f"[分析] 夏普比率: {sharpe_ratio:.2f}")

        # 技术指标
        if 'RSI_14' in self.data.columns:
            rsi = self.data['RSI_14'].iloc[-1]
            self.analysis_results['rsi'] = rsi
            print(f"[分析] RSI(14): {rsi:.2f}")

        # 趋势分析
        if 'MA_20' in self.data.columns and 'MA_50' in self.data.columns:
            ma_20 = self.data['MA_20'].iloc[-1]
            ma_50 = self.data['MA_50'].iloc[-1]

            if current_price > ma_20 > ma_50:
                trend = "上升趋势"
            elif current_price < ma_20 < ma_50:
                trend = "下降趋势"
            else:
                trend = "震荡"

            self.analysis_results['trend'] = trend
            print(f"[分析] 价格趋势: {trend}")

    def generate_signal(self):
        """生成交易信号"""
        print("\n[信号] 生成交易信号...")

        score = 0
        signals = []

        # 趋势分析
        if 'trend' in self.analysis_results:
            if self.analysis_results['trend'] == "上升趋势":
                score += 2
                signals.append("上升趋势")
            elif self.analysis_results['trend'] == "下降趋势":
                score -= 2
                signals.append("下降趋势")

        # RSI分析
        if 'rsi' in self.analysis_results:
            rsi = self.analysis_results['rsi']
            if rsi < 30:
                score += 2
                signals.append("RSI超卖")
            elif rsi > 70:
                score -= 2
                signals.append("RSI超买")

        # 夏普比率
        if 'sharpe_ratio' in self.analysis_results:
            if self.analysis_results['sharpe_ratio'] > 1:
                score += 1
                signals.append("良好的风险调整收益")

        # 生成评级
        if score >= 3:
            rating = "强力买入 (Buy)"
        elif score >= 1:
            rating = "买入 (Overweight)"
        elif score >= -1:
            rating = "持有 (Hold)"
        elif score >= -3:
            rating = "减持 (Underweight)"
        else:
            rating = "卖出 (Sell)"

        self.analysis_results['rating'] = rating
        self.analysis_results['score'] = score
        self.analysis_results['signals'] = signals

        print(f"[信号] 评级: {rating}")
        print(f"[信号] 评分: {score}")
        for sig in signals:
            print(f"       - {sig}")

    def create_visualization(self, ticker, save_path='results'):
        """创建可视化"""
        print(f"\n[可视化] 创建图表...")

        import os
        os.makedirs(save_path, exist_ok=True)

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # 价格走势图
        ax1 = axes[0]
        if 'Close' in self.data.columns:
            ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=2)
            if 'MA_20' in self.data.columns:
                ax1.plot(self.data.index, self.data['MA_20'], label='MA 20', linewidth=1.5, alpha=0.7)
            if 'MA_50' in self.data.columns:
                ax1.plot(self.data.index, self.data['MA_50'], label='MA 50', linewidth=1.5, alpha=0.7)

        ax1.set_title(f'{ticker} - 价格走势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # RSI图
        ax2 = axes[1]
        if 'RSI_14' in self.data.columns:
            ax2.plot(self.data.index, self.data['RSI_14'], label='RSI 14', linewidth=2, color='orange')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='超买 (70)')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='超卖 (30)')
            ax2.fill_between(self.data.index, 30, 70, alpha=0.1, color='gray')

        ax2.set_title('相对强弱指标 (RSI)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        filename = f"{save_path}/{ticker}_analysis.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"[保存] 图表已保存: {filename}")

        plt.close()

    def generate_report(self, ticker):
        """生成分析报告"""
        report = []
        report.append("=" * 80)
        report.append(f"{ticker} - 投资分析报告")
        report.append("=" * 80)
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if 'current_price' in self.analysis_results:
            report.append(f"\n当前价格: ${self.analysis_results['current_price']:.2f}")

        if 'annual_return' in self.analysis_results:
            report.append(f"年化收益率: {self.analysis_results['annual_return']:.2%}")
            report.append(f"年化波动率: {self.analysis_results['annual_volatility']:.2%}")
            report.append(f"夏普比率: {self.analysis_results['sharpe_ratio']:.2f}")

        if 'trend' in self.analysis_results:
            report.append(f"价格趋势: {self.analysis_results['trend']}")

        if 'rsi' in self.analysis_results:
            report.append(f"RSI(14): {self.analysis_results['rsi']:.2f}")

        report.append(f"\n交易评级: {self.analysis_results.get('rating', 'N/A')}")

        if 'signals' in self.analysis_results:
            report.append("\n关键信号:")
            for sig in self.analysis_results['signals']:
                report.append(f"  - {sig}")

        report.append("\n" + "=" * 80)
        report.append("风险提示")
        report.append("=" * 80)
        report.append("1. 本报告仅供参考，不构成投资建议")
        report.append("2. 投资有风险，决策需谨慎")

        return "\n".join(report)

# ==============================================================================
# 主程序
# ==============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("TradingAgents - 简化分析系统")
    print("=" * 80)

    # 读取WRDS账号密码
    wrds_username = "hengyang24"
    wrds_password = "Appleoppo17@"

    # 选择数据源
    print("\n请选择数据源:")
    print("1. WRDS (需要学术账号)")
    print("2. Yahoo Finance (免费，推荐)")

    choice = input("\n请输入选择 (1 或 2，默认2): ").strip() or "2"

    # 输入股票代码
    ticker = input("\n请输入股票代码 (如 AAPL, TSLA): ").strip().upper()

    if not ticker:
        print("[错误] 股票代码不能为空")
        return

    # 获取数据
    data = None

    if choice == "1":
        # 使用WRDS
        wrds = WRDSConnector(wrds_username, wrds_password)
        if wrds.connect():
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            data = wrds.get_stock_data(
                ticker,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
    else:
        # 使用Yahoo Finance
        yahoo = YahooDataSource()
        data = yahoo.get_stock_data(ticker, period='1y')

    if data is None or data.empty:
        print("[错误] 无法获取数据，程序退出")
        return

    # 执行分析
    print("\n" + "=" * 80)
    print("开始分析")
    print("=" * 80)

    analyzer = StockAnalyzer(data)
    analyzer.clean_data()
    analyzer.perform_analysis()
    analyzer.generate_signal()
    analyzer.create_visualization(ticker)

    # 生成报告
    report = analyzer.generate_report(ticker)

    # 保存报告
    import os
    os.makedirs('results', exist_ok=True)

    report_file = f"results/{ticker}_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    # 保存数据
    data_file = f"results/{ticker}_data.csv"
    data.to_csv(data_file)

    # 打印报告
    print("\n" + report)

    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)
    print(f"\n生成的文件:")
    print(f"1. 图表: results/{ticker}_analysis.png")
    print(f"2. 报告: {report_file}")
    print(f"3. 数据: {data_file}")

if __name__ == "__main__":
    try:
        main()
        print("\n按 Enter 键退出...")
        input()
    except Exception as e:
        print(f"\n[错误] 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n按 Enter 键退出...")
        input()
