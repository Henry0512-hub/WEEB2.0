"""
CoinGecko API 数据源
用于获取加密货币价格、市值、交易量等数据
"""

from typing import Annotated
from datetime import datetime, timedelta
import pandas as pd
import requests
import time


class CoinGeckoRateLimitError(Exception):
    """CoinGecko API rate limit exceeded"""
    pass


# CoinGecko API 基础URL
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"


def retry_request(func, max_retries=3, delay=2):
    """
    重试装饰器，用于处理不稳定的网络连接

    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Returns:
        函数执行结果
    """
    for attempt in range(max_retries):
        try:
            return func()
        except (requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                print(f"[警告] 网络错误，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                raise e
    return None


def get_coingecko_id(symbol: str) -> str:
    """
    将加密货币符号转换为CoinGecko ID
    支持主流加密货币的符号到ID映射
    """
    # 常见加密货币映射
    symbol_to_id = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "SOL": "solana",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "SHIB": "shiba-inu",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "LTC": "litecoin",
        "ETC": "ethereum-classic",
        "XLM": "stellar",
        "ALGO": "algorand",
        "VET": "vechain",
        "FIL": "filecoin",
        "NEAR": "near",
        "AAVE": "aave",
        "APT": "aptos",
        "ARB": "arbitrum",
        "OP": "optimism",
        "INJ": "injective-protocol",
        "QNT": "quant-network",
        "IMX": "immutable-x",
        "GRT": "the-graph",
        "SAND": "the-sandbox",
        "MANA": "decentraland",
        "AXS": "axie-infinity",
        "ENJ": "enjincoin",
    }

    # 如果已经是ID格式（包含连字符），直接返回
    if "-" in symbol.lower():
        return symbol.lower()

    # 查找映射
    symbol_upper = symbol.upper()
    if symbol_upper in symbol_to_id:
        return symbol_to_id[symbol_upper]

    # 如果没有找到，尝试通过API搜索
    try:
        url = f"{COINGECKO_API_BASE}/coins/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        coins_list = response.json()
        for coin in coins_list:
            if coin["symbol"].upper() == symbol_upper:
                return coin["id"]

    except Exception as e:
        print(f"[WARNING] 无法从CoinGecko获取 {symbol} 的ID: {e}")

    # 如果找不到，返回小写的symbol作为默认值
    return symbol.lower()


def get_coingecko_price_data(
    symbol: Annotated[str, "加密货币符号"],
    start_date: Annotated[str, "开始日期 yyyy-mm-dd"],
    end_date: Annotated[str, "结束日期 yyyy-mm-dd"],
    vs_currency: str = "usd"
) -> str:
    """
    获取加密货币历史价格数据（OHLCV）

    Args:
        symbol: 加密货币符号（如 BTC, ETH）
        start_date: 开始日期 yyyy-mm-dd
        end_date: 结束日期 yyyy-mm-dd
        vs_currency: 计价货币，默认 usd

    Returns:
        str: 格式化的OHLCV数据
    """
    try:
        # 验证日期格式
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        # 转换为CoinGecko ID
        coin_id = get_coingecko_id(symbol)

        # 转换日期为时间戳
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86400  # 包含结束日

        # CoinGecko API - 获取历史市场数据
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart/range"
        params = {
            "vs_currency": vs_currency,
            "from": start_timestamp,
            "to": end_timestamp
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 解析价格数据
        prices = data.get("prices", [])
        market_caps = data.get("market_caps", [])
        volumes = data.get("total_volumes", [])

        if not prices:
            return f"No data found for cryptocurrency '{symbol}' between {start_date} and {end_date}"

        # 转换为DataFrame
        df_data = []
        for i in range(len(prices)):
            timestamp = prices[i][0] / 1000  # 转换为秒
            date = datetime.fromtimestamp(timestamp)
            df_data.append({
                "Date": date,
                "Open": prices[i][1],  # CoinGecko只有价格，我们使用价格作为Open/Close
                "High": prices[i][1],  # 如果需要更精确的OHLC，可能使用其他API
                "Low": prices[i][1],
                "Close": prices[i][1],
                "Volume": volumes[i][1] if i < len(volumes) else 0,
            })

        df = pd.DataFrame(df_data)
        df.set_index("Date", inplace=True)

        # 按日期聚合（如果一天有多个数据点）
        df = df.resample('D').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # 格式化输出
        csv_string = df.to_csv()

        header = f"# Cryptocurrency data for {symbol.upper()} (CoinGecko: {coin_id}) from {start_date} to {end_date}\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Currency: {vs_currency.upper()}\n\n"

        return header + csv_string

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            raise CoinGeckoRateLimitError("CoinGecko API rate limit exceeded")
        return f"Error fetching data for {symbol}: {e}"
    except Exception as e:
        return f"Error fetching data for {symbol}: {e}"


def get_coingecko_market_info(
    symbol: Annotated[str, "加密货币符号"],
    curr_date: Annotated[str, "当前日期 yyyy-mm-dd"] = None
) -> str:
    """
    获取加密货币市场基本信息

    Args:
        symbol: 加密货币符号
        curr_date: 当前日期（用于兼容，实际不使用）

    Returns:
        str: 格式化的市场信息
    """
    try:
        coin_id = get_coingecko_id(symbol)

        # 获取当前市场数据
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "true",
            "developer_data": "true",
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 提取关键信息
        market_data = data.get("market_data", {})
        community_data = data.get("community_data", {})

        info = []
        info.append(f"=== 加密货币市场信息: {symbol.upper()} ===\n")
        info.append(f"名称: {data.get('name', 'N/A')}")
        info.append(f"符号: {data.get('symbol', 'N/A').upper()}")
        info.append(f"CoinGecko ID: {coin_id}\n")

        info.append("=== 价格信息 ===")
        current_price = market_data.get("current_price", {}).get("usd", "N/A")
        info.append(f"当前价格 (USD): ${current_price:,}" if current_price != "N/A" else f"当前价格: N/A")

        price_change_24h = market_data.get("price_change_percentage_24h", "N/A")
        info.append(f"24小时价格变化: {price_change_24h:.2f}%" if isinstance(price_change_24h, (int, float)) else f"24小时价格变化: N/A")

        price_change_7d = market_data.get("price_change_percentage_7d", "N/A")
        info.append(f"7天价格变化: {price_change_7d:.2f}%" if isinstance(price_change_7d, (int, float)) else f"7天价格变化: N/A")

        price_change_30d = market_data.get("price_change_percentage_30d", "N/A")
        info.append(f"30天价格变化: {price_change_30d:.2f}%" if isinstance(price_change_30d, (int, float)) else f"30天价格变化: N/A")

        info.append("\n=== 市值信息 ===")
        market_cap = market_data.get("market_cap", {}).get("usd", "N/A")
        info.append(f"市值 (USD): ${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else f"市值: N/A")

        market_cap_rank = market_data.get("market_cap_rank", "N/A")
        info.append(f"市值排名: #{market_cap_rank}" if market_cap_rank != "N/A" else "市值排名: N/A")

        fully_diluted_valuation = market_data.get("fully_diluted_valuation", {}).get("usd", "N/A")
        info.append(f"完全稀释估值: ${fully_diluted_valuation:,.0f}" if isinstance(fully_diluted_valuation, (int, float)) else f"完全稀释估值: N/A")

        info.append("\n=== 交易量 ===")
        total_volume = market_data.get("total_volume", {}).get("usd", "N/A")
        info.append(f"24小时交易量 (USD): ${total_volume:,.0f}" if isinstance(total_volume, (int, float)) else f"24小时交易量: N/A")

        info.append("\n=== 供应量 ===")
        circulating_supply = market_data.get("circulating_supply", "N/A")
        info.append(f"流通供应量: {circulating_supply:,.0f}" if isinstance(circulating_supply, (int, float)) else f"流通供应量: N/A")

        total_supply = market_data.get("total_supply", "N/A")
        info.append(f"总供应量: {total_supply:,.0f}" if isinstance(total_supply, (int, float)) else f"总供应量: N/A")

        max_supply = market_data.get("max_supply", "N/A")
        info.append(f"最大供应量: {max_supply:,.0f}" if isinstance(max_supply, (int, float)) else f"最大供应量: 无限制")

        info.append("\n=== 社区数据 ===")
        twitter_followers = community_data.get("twitter_followers", "N/A")
        info.append(f"Twitter粉丝数: {twitter_followers:,}" if isinstance(twitter_followers, int) else "Twitter粉丝数: N/A")

        reddit_subscribers = community_data.get("reddit_subscribers", "N/A")
        info.append(f"Reddit订阅数: {reddit_subscribers:,}" if isinstance(reddit_subscribers, int) else "Reddit订阅数: N/A")

        info.append("\n=== 其他信息 ===")
        genesis_date = data.get("genesis_date", "N/A")
        info.append(f"创世日期: {genesis_date}" if genesis_date else "创世日期: N/A")

        hashing_algorithm = data.get("hashing_algorithm", "N/A")
        info.append(f"哈希算法: {hashing_algorithm}" if hashing_algorithm else "哈希算法: N/A")

        return "\n".join(info)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            raise CoinGeckoRateLimitError("CoinGecko API rate limit exceeded")
        return f"Error fetching market info for {symbol}: {e}"
    except Exception as e:
        return f"Error fetching market info for {symbol}: {e}"


def is_cryptocurrency(symbol: str) -> bool:
    """
    检测符号是否为加密货币

    Args:
        symbol: 资产符号

    Returns:
        bool: 如果是加密货币返回True
    """
    # 主流加密货币列表
    crypto_symbols = {
        "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC",
        "SHIB", "AVAX", "LINK", "UNI", "ATOM", "LTC", "ETC", "XLM", "ALGO",
        "VET", "FIL", "NEAR", "AAVE", "APT", "ARB", "OP", "INJ", "QNT", "IMX",
        "GRT", "SAND", "MANA", "AXS", "ENJ", "PEPE", "WIF", "BONK", "JUP",
        "FET", "RENDER", "RNDR", "SEI", "SUI", "TIA", "INJ", "PYTH"
    }

    return symbol.upper() in crypto_symbols


# 为接口兼容创建别名
get_coingecko_stock_data = get_coingecko_price_data
get_coingecko_fundamentals = get_coingecko_market_info
