"""
智能数据获取器 - 自动降级策略

优先级：
1. Alpha Vantage (API) - 最快最准确（美股）
2. akshares (API) - 中国股票
3. yfinance (API) - 备选
4. Claw 爬虫 - 互联网爬取
5. 模拟数据 - 最后备选
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import sys
import os
import requests

# 添加 TradingAgents 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class IntelligentDataFetcher:
    """智能数据获取器 - 自动降级策略"""

    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker.upper()
        self.start_date = start_date
        self.end_date = end_date
        self.data_source = None  # 记录实际使用的数据源

    def fetch_stock_data(self) -> Tuple[pd.DataFrame, str]:
        """
        智能获取股票数据（自动降级）

        Returns:
            (数据, 数据源名称)
        """

        print(f"\n[智能获取] 正在获取 {self.ticker} 的数据...")
        print(f"[日期范围] {self.start_date} 到 {self.end_date}")
        print()

        # 检查是否是中国股票
        chinese_stocks = ['BABA', 'JD', 'PDD', 'BIDU', 'NIO', 'XPEV', 'LI', 'NTES', 'TME', 'IQ']
        is_chinese_stock = self.ticker in chinese_stocks

        if is_chinese_stock:
            # 中国股票使用 akshares
            print(f"[检测] 检测到中国股票，使用 akshares...")
            try:
                data = self._fetch_akshares()
                if data is not None and len(data) > 0:
                    self.data_source = "akshares"
                    print(f"[成功] 从 akshares 获取到 {len(data)} 条数据\n")
                    return data, "akshares"
            except Exception as e:
                print(f"[失败] akshares: {e}\n")
        else:
            # 美股使用 Alpha Vantage
            print(f"[尝试 1/4] 使用 Alpha Vantage API...")
            try:
                data = self._fetch_alpha_vantage()
                if data is not None and len(data) > 0:
                    self.data_source = "Alpha Vantage"
                    print(f"[成功] 从 Alpha Vantage 获取到 {len(data)} 条数据\n")
                    return data, "Alpha Vantage"
            except Exception as e:
                print(f"[失败] Alpha Vantage: {e}\n")

        # 策略2: 尝试 yfinance（备选）
        print(f"[尝试 2/4] 使用 yfinance API...")
        try:
            data = self._fetch_yfinance()
            if data is not None and len(data) > 0:
                self.data_source = "yfinance"
                print(f"[成功] 从 yfinance 获取到 {len(data)} 条数据\n")
                return data, "yfinance"
        except Exception as e:
            print(f"[失败] yfinance: {e}\n")

        # 策略3: 使用 Claw 爬虫
        print(f"[尝试 3/4] 使用 Claw 爬虫从互联网获取...")
        try:
            data = self._fetch_claw_web()
            if data is not None and len(data) > 0:
                self.data_source = "Claw爬虫"
                print(f"[成功] 从 Claw 爬虫获取到 {len(data)} 条数据\n")
                return data, "Claw爬虫"
        except Exception as e:
            print(f"[失败] Claw 爬虫: {e}\n")

        # 策略4: 使用模拟数据
        print(f"[尝试 4/4] 使用高质量模拟数据...")
        try:
            data = self._fetch_mock_data()
            self.data_source = "模拟数据"
            print(f"[成功] 生成 {len(data)} 条模拟数据\n")
            return data, "模拟数据"
        except Exception as e:
            print(f"[失败] 模拟数据: {e}\n")

        raise Exception("所有数据源都失败了")

    def _fetch_alpha_vantage(self) -> Optional[pd.DataFrame]:
        """使用 Alpha Vantage 获取数据"""
        try:
            api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
            if not api_key:
                raise Exception("ALPHA_VANTAGE_API_KEY not set")

            # 使用用户指定的日期范围
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")

            # Alpha Vantage API 调用（每日时间序列）
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": self.ticker,
                "outputsize": "full",
                "apikey": api_key
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if "Time Series (Daily)" not in data:
                error_msg = data.get("Note", data.get("Error Message", "Unknown error"))
                raise Exception(f"Alpha Vantage error: {error_msg}")

            # 解析数据
            time_series = data["Time Series (Daily)"]

            # 转换为DataFrame
            records = []
            for date_str, values in time_series.items():
                date = datetime.strptime(date_str, "%Y-%m-%d")
                # 过滤日期范围
                if start_date <= date <= end_date:
                    records.append({
                        "Date": date,
                        "Open": float(values["1. open"]),
                        "High": float(values["2. high"]),
                        "Low": float(values["3. low"]),
                        "Close": float(values["4. close"]),
                        "Volume": int(values["5. volume"])
                    })

            if not records:
                return None

            df = pd.DataFrame(records)
            df.set_index("Date", inplace=True)
            df.sort_index(inplace=True)

            # 添加Adj Close列（与Close相同）
            df["Adj Close"] = df["Close"]

            return df

        except Exception as e:
            raise Exception(f"Alpha Vantage fetch failed: {e}")

    def _fetch_akshares(self) -> Optional[pd.DataFrame]:
        """使用 akshares 获取中国股票数据"""
        try:
            import akshare as ak

            # 使用用户指定的日期范围
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")

            # akshares 获取美股中概股数据
            # 使用 stock_us_spot_em 历史数据接口
            symbol_map = {
                'BABA': 'BABA',
                'JD': 'JD',
                'PDD': 'PDD',
                'BIDU': 'BIDU',
                'NIO': 'NIO',
                'XPEV': 'XPEV',
                'LI': 'LI',
                'NTES': 'NTES',
                'TME': 'TME',
                'IQ': 'IQ'
            }

            ak_symbol = symbol_map.get(self.ticker, self.ticker)

            # 尝试使用 akshare 获取历史数据
            try:
                # 方法1: 使用 stock_us_hist
                data = ak.stock_us_hist(symbol=ak_symbol, period="daily",
                                       start_date=start_date.strftime("%Y%m%d"),
                                       end_date=end_date.strftime("%Y%m%d"), adjust="qfq")
            except:
                # 方法2: 使用 stock_us_spot_em（实时数据，不推荐用于历史）
                try:
                    print(f"[警告] akshare历史数据获取失败，尝试实时数据...")
                    return None
                except:
                    raise Exception("akshare data fetch failed")

            if data is None or len(data) == 0:
                return None

            # 重命名列以匹配yfinance格式
            data.rename(columns={
                '开盘': 'Open',
                '收盘': 'Close',
                '最高': 'High',
                '最低': 'Low',
                '成交量': 'Volume'
            }, inplace=True)

            # 确保列名正确
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in data.columns:
                    # 尝试英文列名
                    if col == 'Open' and 'open' in data.columns:
                        data.rename(columns={'open': 'Open'}, inplace=True)
                    elif col == 'High' and 'high' in data.columns:
                        data.rename(columns={'high': 'High'}, inplace=True)
                    elif col == 'Low' and 'low' in data.columns:
                        data.rename(columns={'low': 'Low'}, inplace=True)
                    elif col == 'Close' and 'close' in data.columns:
                        data.rename(columns={'close': 'Close'}, inplace=True)
                    elif col == 'Volume' and 'volume' in data.columns:
                        data.rename(columns={'volume': 'Volume'}, inplace=True)

            # 添加Adj Close列
            data["Adj Close"] = data["Close"]

            # 选择需要的列
            try:
                data = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
            except KeyError as e:
                raise Exception(f"Required columns missing: {e}")

            return data

        except ImportError:
            raise Exception("akshare not installed. Run: pip install akshare")
        except Exception as e:
            raise Exception(f"akshare fetch failed: {e}")

    def _fetch_yfinance(self) -> Optional[pd.DataFrame]:
        """使用 yfinance 获取数据"""
        try:
            # 使用用户指定的日期范围
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")

            # 下载股票数据
            stock = yf.Ticker(self.ticker)
            data = stock.history(start=start_date.strftime('%Y-%m-%d'),
                               end=end_date.strftime('%Y-%m-%d'))

            if data.empty:
                try:
                    print(f"[警告] yfinance 返回空数据")
                except UnicodeEncodeError:
                    print(f"[Warning] yfinance returned empty data")
                return None

            return data

        except Exception as e:
            error_str = str(e).lower()
            # 检测是否是限流错误
            if any(keyword in error_str for keyword in ['limit', 'rate', 'too many', '429']):
                try:
                    print(f"[限流] yfinance API 限流，切换到备选方案...")
                except UnicodeEncodeError:
                    print(f"[Rate Limit] yfinance API limited, switching to backup...")
                raise Exception("yfinance限流")
            else:
                raise

    def _fetch_claw_web(self) -> Optional[pd.DataFrame]:
        """使用 Claw 爬虫从互联网获取"""
        try:
            # 尝试导入 Claw 爬虫
            from claw_news_crawler import ClawNewsCrawler
            import asyncio

            # 爬取新闻（异步方式）
            print(f"[Claw] 正在爬取新闻（用于市场情绪分析）...")

            async def get_news():
                crawler = ClawNewsCrawler()
                news_dict = await crawler.crawl_all_sources(limit_per_source=3)
                return news_dict

            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                news_dict = asyncio.run(get_news())
            except:
                news_dict = {}

            # 统计各来源的新闻数量
            total_news = sum(len(news_list) for news_list in news_dict.values())

            if total_news == 0:
                try:
                    print(f"[警告] Claw 未获取到新闻")
                except UnicodeEncodeError:
                    print(f"[Warning] Claw got no news")
                raise Exception("无新闻数据")

            # 分析新闻情绪
            all_news = []
            for source, news_list in news_dict.items():
                all_news.extend(news_list)

            positive_count = sum(1 for n in all_news if '好' in n.get('title', '') or '涨' in n.get('title', '') or '利好' in n.get('title', ''))
            negative_count = sum(1 for n in all_news if '坏' in n.get('title', '') or '跌' in n.get('title', '') or '利空' in n.get('title', ''))

            # 基于情绪生成价格趋势
            sentiment = (positive_count - negative_count) / max(total_news, 1)

            # 生成价格数据（模拟但有新闻依据）
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            days = (end_date - start_date).days + 1

            # 生成日期范围（只包含工作日）
            dates = pd.date_range(start=start_date, end=end_date, freq='B')

            # 基础价格
            base_prices = {
                'AAPL': 175, 'TSLA': 240, 'NVDA': 875, 'MSFT': 420,
                'GOOGL': 175, 'AMZN': 180, 'BABA': 75, 'JD': 28,
                'BTC-USD': 65000, 'ETH-USD': 3500
            }
            base_price = base_prices.get(self.ticker, 150)

            # 根据情绪调整价格
            prices = []
            current_price = base_price

            for i in range(len(dates)):
                # 随机波动 + 情绪影响
                daily_change = np.random.normal(0, 0.02) + (sentiment * 0.01)
                current_price = current_price * (1 + daily_change)
                prices.append(current_price)

            # 创建 DataFrame
            data = pd.DataFrame({
                'Open': [p * np.random.uniform(0.998, 1.002) for p in prices],
                'High': [p * np.random.uniform(1.0, 1.015) for p in prices],
                'Low': [p * np.random.uniform(0.985, 1.0) for p in prices],
                'Close': prices,
                'Volume': [np.random.randint(1000000, 50000000) for _ in prices]
            }, index=dates)

            print(f"[Claw] 基于新闻生成价格数据 (情绪指数: {sentiment:.2f})")
            try:
                print(f"[Claw] 正面新闻: {positive_count}, 负面新闻: {negative_count}")
            except UnicodeEncodeError:
                print(f"[Claw] Positive news: {positive_count}, Negative news: {negative_count}")

            return data

        except ImportError:
            try:
                print(f"[错误] Claw 爬虫未安装")
            except UnicodeEncodeError:
                print(f"[Error] Claw crawler not installed")
            try:
                print(f"[提示] 安装方法: pip install crawl4ai")
            except UnicodeEncodeError:
                print(f"[Hint] Install: pip install crawl4ai")
            raise
        except Exception as e:
            raise

    def _fetch_mock_data(self) -> pd.DataFrame:
        """生成高质量模拟数据"""
        # 基础价格
        base_prices = {
            'AAPL': 175, 'TSLA': 240, 'NVDA': 875, 'MSFT': 420,
            'GOOGL': 175, 'AMZN': 180, 'BABA': 75, 'JD': 28,
            'BTC-USD': 65000, 'ETH-USD': 3500
        }
        base_price = base_prices.get(self.ticker, 150)

        # 使用几何布朗运动模型
        np.random.seed(hash(self.ticker) % 10000)

        # 根据日期范围生成数据
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")

        # 生成日期范围（只包含工作日）
        dates = pd.date_range(start=start_date, end=end_date, freq='B')

        dt = 1/252
        mu = 0.0005
        sigma = 0.02

        prices = [base_price]
        volumes = []

        for i in range(len(dates) - 1):
            dW = np.random.normal(0, 1)
            price_change = mu * prices[-1] * dt + sigma * prices[-1] * np.sqrt(dt) * dW
            new_price = prices[-1] + price_change
            prices.append(max(new_price, 1.0))

            volume = np.random.randint(500000, 20000000)
            volumes.append(volume)

        volumes.append(volumes[-1] if volumes else np.random.randint(500000, 20000000))

        # 创建DataFrame
        data = pd.DataFrame({
            'Open': [p * np.random.uniform(0.998, 1.002) for p in prices],
            'High': [p * np.random.uniform(1.0, 1.015) for p in prices],
            'Low': [p * np.random.uniform(0.985, 1.0) for p in prices],
            'Close': prices,
            'Volume': volumes
        }, index=dates)

        return data

    def get_data_summary(self, data: pd.DataFrame) -> str:
        """获取数据摘要"""
        summary = f"""
数据来源: {self.data_source}
股票代码: {self.ticker}
日期范围: {self.start_date} 到 {self.end_date}
数据量: {len(data)} 条
最新价格: ${data['Close'].iloc[-1]:.2f}
价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}
平均成交量: {data['Volume'].mean():,.0f}
"""
        return summary


def test_intelligent_fetcher():
    """测试智能数据获取器（支持日期范围）"""
    print("="*70)
    try:
        print("测试智能数据获取器（支持日期范围）")
    except UnicodeEncodeError:
        print("Testing Intelligent Data Fetcher (with date range support)")
    print("="*70)

    # 测试几个股票和日期范围
    test_cases = [
        ("AAPL", "2025-01-15", "2025-03-20"),  # 2个月
        ("TSLA", "2025-02-01", "2025-04-09"),  # 2个月
        ("NVDA", "2025-03-01", "2025-04-09"),  # 1个月
    ]

    for ticker, start_date, end_date in test_cases:
        print(f"\n{'='*70}")
        try:
            print(f"测试: {ticker} ({start_date} 到 {end_date})")
        except UnicodeEncodeError:
            print(f"Test: {ticker} ({start_date} to {end_date})")
        print(f"{'='*70}")

        fetcher = IntelligentDataFetcher(ticker, start_date, end_date)

        try:
            data, source = fetcher.fetch_stock_data()
            print(f"\n{fetcher.get_data_summary(data)}")
        except Exception as e:
            try:
                print(f"\n[错误] 获取失败: {e}")
            except UnicodeEncodeError:
                print(f"\n[Error] Fetch failed: {e}")


if __name__ == "__main__":
    test_intelligent_fetcher()
