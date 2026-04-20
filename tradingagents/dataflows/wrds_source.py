"""
WRDS数据源 - 连接Wharton Research Data Services
支持CRSP (股票价格) 和 Compustat (财务数据)
"""

from typing import Annotated
from datetime import datetime, timedelta
import pandas as pd
from tradingagents.utils.credentials import load_wrds_credentials
import wrds


def _connect_wrds_noninteractive(username: str, password: str):
    """多策略连接 WRDS，尽可能避免交互并提高成功率。"""
    import os
    import psycopg2
    import sqlalchemy

    last_err = None
    old_user = os.environ.get('PGUSER')
    old_pwd = os.environ.get('PGPASSWORD')
    old_ssl = os.environ.get('PGSSLMODE')
    old_host = os.environ.get('PGHOST')
    old_port = os.environ.get('PGPORT')
    old_db = os.environ.get('PGDATABASE')

    try:
        # 固定 WRDS 连接参数
        os.environ['PGUSER'] = username
        os.environ['PGPASSWORD'] = password
        os.environ['PGSSLMODE'] = 'require'
        os.environ['PGHOST'] = 'wrds-pgdata.wharton.upenn.edu'
        os.environ['PGPORT'] = '9737'
        os.environ['PGDATABASE'] = 'wrds'

        # 策略1：wrds Connection 非交互连接（禁止 fallback 到 getpass）
        try:
            db = wrds.Connection(
                autoconnect=False,
                wrds_username=username,
                wrds_password=password,
            )
            db._Connection__make_sa_engine_conn(raise_err=True)
            if getattr(db, "engine", None) is None or getattr(db, "connection", None) is None:
                raise ConnectionError("WRDS non-interactive connect failed")
            return db
        except Exception as e1:
            last_err = e1

        # 策略2：psycopg2 + SSL 直连，再挂到 wrds.Connection 对象
        try:
            conn = psycopg2.connect(
                host='wrds-pgdata.wharton.upenn.edu',
                port=9737,
                database='wrds',
                user=username,
                password=password,
                sslmode='require',
            )
            engine = sqlalchemy.create_engine(
                "postgresql+psycopg2://",
                creator=lambda: conn,
            )
            db = wrds.Connection(
                autoconnect=False,
                wrds_username=username,
                wrds_password=password,
            )
            db.engine = engine
            db.connection = engine.connect()
            return db
        except Exception as e2:
            last_err = e2
            raise ConnectionError(f"WRDS non-interactive connect failed: {e2}") from last_err

    finally:
        # 恢复环境变量
        if old_user is not None:
            os.environ['PGUSER'] = old_user
        elif 'PGUSER' in os.environ:
            del os.environ['PGUSER']

        if old_pwd is not None:
            os.environ['PGPASSWORD'] = old_pwd
        elif 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']
        if old_ssl is not None:
            os.environ['PGSSLMODE'] = old_ssl
        elif 'PGSSLMODE' in os.environ:
            del os.environ['PGSSLMODE']
        if old_host is not None:
            os.environ['PGHOST'] = old_host
        elif 'PGHOST' in os.environ:
            del os.environ['PGHOST']
        if old_port is not None:
            os.environ['PGPORT'] = old_port
        elif 'PGPORT' in os.environ:
            del os.environ['PGPORT']
        if old_db is not None:
            os.environ['PGDATABASE'] = old_db
        elif 'PGDATABASE' in os.environ:
            del os.environ['PGDATABASE']


class WRDSConnectionError(Exception):
    """WRDS连接错误"""
    pass


class WRDSQueryError(Exception):
    """WRDS查询错误"""
    pass

class WRDSConnection:
    """WRDS数据库连接管理器"""

    def __init__(self):
        self.db = None
        self._connected = False

    def connect(self):
        """建立WRDS连接"""
        if self._connected:
            return self.db

        try:
            creds = load_wrds_credentials()
            if not creds:
                raise ConnectionError(
                    "WRDS 未配置：请在 is/wrds.txt 写入 username/password，"
                    "或设置环境变量 WRDS_USERNAME、WRDS_PASSWORD。"
                )
            u, p = creds["username"], creds["password"]
            self.db = _connect_wrds_noninteractive(u, p)
            self._connected = True
            return self.db

        except Exception as e:
            raise ConnectionError(f"无法连接到WRDS: {str(e)}")

    def close(self):
        """关闭连接"""
        if self.db:
            self.db.close()
            self._connected = False

# Global WRDS handle (wrds.Connection). Do not close the underlying connection
# from call sites — closing poisons this singleton until reconnect.
_wrds_connection = None


def _wrds_engine_dead(db) -> bool:
    if db is None:
        return True
    eng = getattr(db, "engine", None)
    if eng is None:
        return True
    conn = getattr(db, "connection", None)
    if conn is None:
        return True
    try:
        return bool(getattr(conn, "closed", False))
    except Exception:
        return True


def invalidate_wrds_connection() -> None:
    """Mark global WRDS connection stale (e.g. after remote idle disconnect)."""
    global _wrds_connection
    if _wrds_connection is not None:
        try:
            _wrds_connection.close()
        except Exception:
            pass
    _wrds_connection = None


def get_wrds_connection():
    """Return a live wrds.Connection; reconnect if the previous one was closed."""
    global _wrds_connection

    if _wrds_connection is None or not _wrds_connection._connected:
        _wrds_connection = WRDSConnection()
        _wrds_connection.connect()
    db = _wrds_connection.db
    if _wrds_engine_dead(db):
        invalidate_wrds_connection()
        _wrds_connection = WRDSConnection()
        _wrds_connection.connect()
        db = _wrds_connection.db

    return db


def get_stock_data_wrds(
    symbol: Annotated[str, "Stock ticker symbol (e.g., AAPL)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    从WRDS CRSP数据库获取股票价格数据

    Args:
        symbol: 股票代码
        start_date: 开始日期 (yyyy-mm-dd)
        end_date: 结束日期 (yyyy-mm-dd)

    Returns:
        CSV格式的股票数据
    """
    try:
        db = get_wrds_connection()

        # CRSP数据库查询
        # 首先获取股票的permno (CRSP永久编号)
        symbol_sql = f"""
        SELECT permno, permco, ticker, comnam
        FROM crsp.stocknames
        WHERE ticker = '{symbol.upper()}'
        ORDER BY namedt DESC
        LIMIT 1
        """

        stock_info = db.raw_sql(symbol_sql)

        if stock_info.empty:
            return f"Error: Stock symbol '{symbol}' not found in CRSP database"

        permno = stock_info['permno'].iloc[0]

        # 获取股票价格数据
        price_sql = f"""
        SELECT date, permno, prc AS close, bid AS bid, ask AS ask,
               shrout AS shares, vol AS volume
        FROM crsp.dsf
        WHERE permno = {permno}
        AND date >= '{start_date}'
        AND date <= '{end_date}'
        ORDER BY date
        """

        price_data = db.raw_sql(price_sql, date_cols=['date'])

        if price_data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

        # 处理数据：CRSP价格是负数表示bid/ask的平均值
        price_data['close'] = price_data['close'].abs()

        # 计算OHLC (CRSP只有收盘价，这里简化处理)
        price_data = price_data[['date', 'close', 'volume']].copy()
        price_data = price_data.rename(columns={'date': 'Date'})
        price_data = price_data.set_index('Date')

        # 添加缺失的OHLC列（使用收盘价）
        price_data['Open'] = price_data['close']
        price_data['High'] = price_data['close']
        price_data['Low'] = price_data['close']
        price_data['Adj Close'] = price_data['close']

        # 重新排列列顺序
        price_data = price_data[['Open', 'High', 'Low', 'close', 'Adj Close', 'volume']]
        price_data = price_data.rename(columns={'close': 'Close'})

        # 转换为CSV
        csv_string = price_data.to_csv()

        # 添加头部信息
        header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date} (Source: WRDS CRSP)\n"
        header += f"# Total records: {len(price_data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error retrieving WRDS data: {str(e)}"


def get_fundamentals_wrds(
    symbol: Annotated[str, "Stock ticker symbol"],
) -> str:
    """
    从WRDS Compustat数据库获取基本面数据

    Args:
        symbol: 股票代码

    Returns:
        CSV格式的基本面数据
    """
    try:
        db = get_wrds_connection()

        # Compustat - 首先通过gvkey (公司关键标识符)查询
        # 这里使用CRSP-Compustat链接表
        link_sql = f"""
        SELECT l.gvkey, l.lpermno, l.linktype, l.linkprim,
               c.conm AS company_name
        FROM crsp.ccmxpf_linktable l
        JOIN comp.company c ON l.gvkey = c.gvkey
        JOIN crsp.stocknames s ON l.lpermno = s.permno
        WHERE s.ticker = '{symbol.upper()}'
        AND l.linkprim IN ('P', 'C')
        AND l.linktype IN ('LU', 'LC')
        ORDER BY l.linkdt DESC
        LIMIT 1
        """

        link_data = db.raw_sql(link_sql)

        if link_data.empty:
            # 尝试直接从Compustat查找
            comp_sql = f"""
            SELECT gvkey, conm AS company_name
            FROM comp.company
            WHERE tic = '{symbol.upper()}'
            AND subdim = 'C'
            LIMIT 1
            """
            comp_data = db.raw_sql(comp_sql)

            if comp_data.empty:
                return f"Error: Company '{symbol}' not found in Compustat database"
            else:
                gvkey = comp_data['gvkey'].iloc[0]
                company_name = comp_data['company_name'].iloc[0]
        else:
            gvkey = link_data['gvkey'].iloc[0]
            company_name = link_data['company_name'].iloc[0]

        # 获取最近的财务数据
        fund_sql = f"""
        SELECT datadate, fyear,
               sale AS revenue, ni AS net_income,
               at AS total_assets, lt AS total_liabilities,
               ceq AS total_equity
        FROM comp.funda
        WHERE gvkey = '{gvkey}'
        ORDER BY datadate DESC
        LIMIT 20
        """

        fund_data = db.raw_sql(fund_sql, date_cols=['datadate'])

        if fund_data.empty:
            return f"No fundamental data found for {symbol}"

        # 转换为CSV
        csv_string = fund_data.to_csv()

        # 添加头部信息
        header = f"# Fundamental data for {symbol.upper()} - {company_name} (Source: WRDS Compustat)\n"
        header += f"# Total records: {len(fund_data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error retrieving WRDS fundamentals: {str(e)}"


def get_balance_sheet_wrds(
    symbol: Annotated[str, "Stock ticker symbol"],
    year: Annotated[int, "Fiscal year (optional, defaults to most recent)"] = None,
) -> str:
    """
    从WRDS Compustat获取资产负债表数据

    Args:
        symbol: 股票代码
        year: 财年 (可选，默认最新)

    Returns:
        CSV格式的资产负债表数据
    """
    try:
        db = get_wrds_connection()

        # 获取gvkey
        comp_sql = f"""
        SELECT gvkey, conm
        FROM comp.company
        WHERE tic = '{symbol.upper()}'
        LIMIT 1
        """

        comp_data = db.raw_sql(comp_sql)

        if comp_data.empty:
            return f"Error: Company '{symbol}' not found in Compustat"

        gvkey = comp_data['gvkey'].iloc[0]

        # 构建查询条件
        year_filter = f"AND fyear = {year}" if year else ""

        # 资产负债表数据
        bs_sql = f"""
        SELECT datadate, fyear,
               at AS total_assets, lt AS total_liabilities,
               ceq AS total_equity
        FROM comp.funda
        WHERE gvkey = '{gvkey}'
        {year_filter}
        ORDER BY datadate DESC
        LIMIT 10
        """

        bs_data = db.raw_sql(bs_sql, date_cols=['datadate'])

        if bs_data.empty:
            return f"No balance sheet data found for {symbol}"

        csv_string = bs_data.to_csv()
        header = f"# Balance Sheet for {symbol.upper()} (Source: WRDS Compustat)\n"
        header += f"# Records: {len(bs_data)}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error retrieving balance sheet: {str(e)}"


def get_income_statement_wrds(
    symbol: Annotated[str, "Stock ticker symbol"],
    year: Annotated[int, "Fiscal year (optional)"] = None,
) -> str:
    """
    从WRDS Compustat获取利润表数据

    Args:
        symbol: 股票代码
        year: 财年 (可选)

    Returns:
        CSV格式的利润表数据
    """
    try:
        db = get_wrds_connection()

        # 获取gvkey
        comp_sql = f"""
        SELECT gvkey, conm
        FROM comp.company
        WHERE tic = '{symbol.upper()}'
        LIMIT 1
        """

        comp_data = db.raw_sql(comp_sql)

        if comp_data.empty:
            return f"Error: Company '{symbol}' not found"

        gvkey = comp_data['gvkey'].iloc[0]

        year_filter = f"AND fyear = {year}" if year else ""

        # 利润表数据
        is_sql = f"""
        SELECT datadate, fyear,
               sale AS revenue, ni AS net_income
        FROM comp.funda
        WHERE gvkey = '{gvkey}'
        {year_filter}
        ORDER BY datadate DESC
        LIMIT 10
        """

        is_data = db.raw_sql(is_sql, date_cols=['datadate'])

        if is_data.empty:
            return f"No income statement data found for {symbol}"

        csv_string = is_data.to_csv()
        header = f"# Income Statement for {symbol.upper()} (Source: WRDS Compustat)\n"
        header += f"# Records: {len(is_data)}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error retrieving income statement: {str(e)}"


def get_cashflow_wrds(
    symbol: Annotated[str, "Stock ticker symbol"],
    year: Annotated[int, "Fiscal year (optional)"] = None,
) -> str:
    """
    从WRDS Compustat获取现金流量表数据

    Args:
        symbol: 股票代码
        year: 财年 (可选)

    Returns:
        CSV格式的现金流量表数据
    """
    try:
        db = get_wrds_connection()

        comp_sql = f"""
        SELECT gvkey, conm
        FROM comp.company
        WHERE tic = '{symbol.upper()}'
        LIMIT 1
        """

        comp_data = db.raw_sql(comp_sql)

        if comp_data.empty:
            return f"Error: Company '{symbol}' not found"

        gvkey = comp_data['gvkey'].iloc[0]

        year_filter = f"AND fyear = {year}" if year else ""

        # 现金流量表数据
        cf_sql = f"""
        SELECT datadate, fyear,
               che AS cash_equivalents
        FROM comp.funda
        WHERE gvkey = '{gvkey}'
        {year_filter}
        ORDER BY datadate DESC
        LIMIT 10
        """

        cf_data = db.raw_sql(cf_sql, date_cols=['datadate'])

        if cf_data.empty:
            return f"No cashflow data found for {symbol}"

        csv_string = cf_data.to_csv()
        header = f"# Cash Flow Statement for {symbol.upper()} (Source: WRDS Compustat)\n"
        header += f"# Records: {len(cf_data)}\n\n"

        return header + csv_string

    except Exception as e:
        return f"Error retrieving cashflow statement: {str(e)}"


# 导出函数列表
__all__ = [
    'get_stock_data_wrds',
    'get_fundamentals_wrds',
    'get_balance_sheet_wrds',
    'get_income_statement_wrds',
    'get_cashflow_wrds',
    'get_wrds_connection',
]
