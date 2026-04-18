"""
akshare 新闻数据适配器
用于获取中国股市新闻
"""

import akshare as ak
from datetime import datetime, timedelta


def get_sina_news(stock_code: str, limit: int = 10) -> str:
    """
    获取新浪财经新闻（中国股市）

    Args:
        stock_code: 股票代码（如 "000001"）
        limit: 新闻数量

    Returns:
        格式化的新闻字符串
    """
    try:
        # 获取个股新闻
        news_df = ak.stock_news_em(symbol=stock_code)

        if news_df.empty:
            return f"No news found for {stock_code}"

        news_str = f"## {stock_code} News (Sina Finance):\n\n"

        # 取前 limit 条
        for idx, row in news_df.head(limit).iterrows():
            title = row.get('新闻标题', 'No title')
            content = row.get('新闻内容', '')
            time = row.get('发布时间', '')

            news_str += f"### {title}\n"
            if time:
                news_str += f"Time: {time}\n"
            if content:
                news_str += f"{content}\n"
            news_str += "\n"

        return news_str

    except Exception as e:
        return f"Error fetching Sina news: {str(e)}"


def get_eastmoney_news(stock_code: str, limit: int = 10) -> str:
    """
    获取东方财富新闻（中国股市）

    Args:
        stock_code: 股票代码
        limit: 新闻数量

    Returns:
        格式化的新闻字符串
    """
    try:
        # 获取个股新闻
        news_df = ak.stock_news_em(symbol=stock_code)

        if news_df.empty:
            return f"No news found for {stock_code}"

        news_str = f"## {stock_code} News (Eastmoney):\n\n"

        for idx, row in news_df.head(limit).iterrows():
            news_str += f"### {row.get('新闻标题', 'No title')}\n"
            news_str += f"{row.get('新闻内容', '')}\n"
            news_str += f"Time: {row.get('发布时间', '')}\n\n"

        return news_str

    except Exception as e:
        return f"Error fetching Eastmoney news: {str(e)}"


def get_global_news_china(limit: int = 20) -> str:
    """
    获取中国财经要闻

    Args:
        limit: 新闻数量

    Returns:
        格式化的新闻字符串
    """
    try:
        # 获取财经要闻
        news_df = ak.stock_news_em(symbol="A股")

        if news_df.empty:
            return "No China market news found"

        news_str = "## China Market News:\n\n"

        for idx, row in news_df.head(limit).iterrows():
            news_str += f"### {row.get('新闻标题', 'No title')}\n"
            news_str += f"{row.get('新闻内容', '')}\n"
            news_str += f"Time: {row.get('发布时间', '')}\n\n"

        return news_str

    except Exception as e:
        return f"Error fetching China market news: {str(e)}"


def get_stock_news_yjc(stock_code: str, limit: int = 10) -> str:
    """
    获取同花顺新闻

    Args:
        stock_code: 股票代码
        limit: 新闻数量

    Returns:
        格式化的新闻字符串
    """
    try:
        # 获取新闻
        news_df = ak.stock_news_em(symbol=stock_code)

        if news_df.empty:
            return f"No news found for {stock_code}"

        news_str = f"## {stock_code} News (10jqka):\n\n"

        for idx, row in news_df.head(limit).iterrows():
            news_str += f"### {row.get('新闻标题', 'No title')}\n"
            news_str += f"{row.get('新闻内容', '')}\n\n"

        return news_str

    except Exception as e:
        return f"Error fetching 10jqka news: {str(e)}"


# 综合新闻获取函数
def get_chinese_stock_news(stock_code: str, limit: int = 10) -> str:
    """
    综合获取中国股市新闻

    Args:
        stock_code: 股票代码（如 "000001"）
        limit: 每个来源的新闻数量

    Returns:
        综合新闻字符串
    """
    news_str = f"## {stock_code} News Summary (China):\n\n"

    # 尝试多个来源
    sources = [
        ("Sina", lambda: get_sina_news(stock_code, limit)),
        ("Eastmoney", lambda: get_eastmoney_news(stock_code, limit)),
        ("10jqka", lambda: get_stock_news_yjc(stock_code, limit)),
    ]

    for source_name, source_func in sources:
        try:
            source_news = source_func()
            if not source_news.startswith("Error") and not source_news.startswith("No news"):
                news_str += f"### Source: {source_name}\n"
                news_str += source_news + "\n"
        except:
            continue

    return news_str
