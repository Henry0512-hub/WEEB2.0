"""
EFinance数据源模块 - 用于获取中国A股数据
支持A股、港股等中国市场的股票数据

优先使用仓库内 ``vendor/efinance``（Micro-sheep/efinance 源码），见 `tradingagents.utils.efinance_vendor`。
"""

from typing import Annotated
from datetime import datetime, timedelta
import pandas as pd

from tradingagents.utils.efinance_vendor import ensure_vendored_efinance

ensure_vendored_efinance()
import efinance as ef


def _convert_a_share_code(symbol: str) -> str:
    """
    将股票代码转换为efinance格式

    Args:
        symbol: 股票代码 (如: 600519.SS, 000001.SZ)

    Returns:
        efinance格式的股票代码 (如: 600519, 000001)
    """
    # 移除后缀 (.SS, .SZ 等)
    code = symbol.split('.')[0]
    return code


def get_efinance_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    """
    使用EFinance获取A股历史价格数据

    Args:
        symbol: 股票代码 (如: 600519.SS, 000001.SZ)
        start_date: 开始日期 (yyyy-mm-dd)
        end_date: 结束日期 (yyyy-mm-dd)

    Returns:
        str: 格式化的CSV数据字符串
    """

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return f"Invalid date format. Please use yyyy-mm-dd format."

    # 转换股票代码
    code = _convert_a_share_code(symbol)

    try:
        # 获取历史数据（不使用日期参数，因为efinance的日期参数可能不工作）
        data = ef.stock.get_quote_history(code)

        # 检查是否获取到数据
        if data is None or data.empty:
            return f"No data found for symbol '{symbol}' (code: {code})"

        # 确保有日期列
        date_col = None
        for col in ['日期', 'Date']:
            if col in data.columns:
                date_col = col
                break

        if date_col is None:
            return f"No date column found in data for '{symbol}'. Available columns: {list(data.columns)}"

        # 转换日期列并过滤
        data[date_col] = pd.to_datetime(data[date_col])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        # 过滤日期范围
        data = data[(data[date_col] >= start_dt) & (data[date_col] <= end_dt)]

        # 再次检查是否有数据
        if data.empty:
            return f"No data found for symbol '{symbol}' (code: {code}) between {start_date} and {end_date}"

        # 重命名列以匹配yfinance格式
        column_mapping = {
            '收盘': 'Close',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '涨跌幅': 'Change%',
            '日期': 'Date'
        }

        # 只保留需要的列
        required_columns = ['日期', '开盘', '最高', '最低', '收盘', '成交量']
        available_columns = [col for col in required_columns if col in data.columns]

        if not available_columns:
            return f"Required columns not found in data for symbol '{symbol}'"

        data = data[available_columns].copy()
        data.rename(columns=column_mapping, inplace=True)

        # 设置日期为索引
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)

        # 确保数据按日期排序
        data.sort_index(inplace=True)

        # 添加Adj Close列（对于A股，Adj Close等于Close）
        if 'Close' in data.columns and 'Adj Close' not in data.columns:
            data['Adj Close'] = data['Close']

        # 重新排列列顺序以匹配yfinance格式
        column_order = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        available_column_order = [col for col in column_order if col in data.columns]
        data = data[available_column_order]

        # 数值列保留2位小数
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        for col in numeric_columns:
            if col in data.columns:
                data[col] = data[col].round(2)

        # 转换为CSV字符串
        csv_string = data.to_csv()

        # 添加头部信息
        header = f"# Stock data for {symbol.upper()} (EFinance) from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error fetching data for '{symbol}': {str(e)}"


def get_efinance_fundamentals(symbol: str) -> str:
    """
    获取A股基本面数据

    Args:
        symbol: 股票代码

    Returns:
        str: 格式化的基本面数据
    """
    try:
        code = _convert_a_share_code(symbol)

        # 获取股票基本信息
        base_info = ef.stock.get_base_info(code)

        if base_info is None or base_info.empty:
            return f"No fundamental data found for symbol '{symbol}'"

        result = f"# Fundamental Data for {symbol.upper()}\n\n"
        result += base_info.to_string()

        return result

    except Exception as e:
        return f"Error fetching fundamentals for '{symbol}': {str(e)}"


def is_a_share_stock(symbol: str) -> bool:
    """
    检测是否为A股代码

    Args:
        symbol: 股票代码

    Returns:
        bool: 是否为A股代码
    """
    # A股代码格式: 6位数字 + .SS 或 .SZ
    # 或者单纯的6位数字（000001-600xxx等）
    import re

    # 检查是否有.SS或.SZ后缀
    if '.' in symbol:
        parts = symbol.split('.')
        if len(parts) == 2:
            code, market = parts
            # 检查是否为6位数字且后缀为SS或SZ
            if code.isdigit() and len(code) == 6 and market.upper() in ['SS', 'SZ']:
                return True

    # 检查是否为6位数字（纯A股代码）
    if symbol.isdigit() and len(symbol) == 6:
        return True

    return False
