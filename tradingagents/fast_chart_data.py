"""
ACCE v2.0 - 快速图表数据模块
使用yfinance/akshare获取数据，生成富途牛牛风格的专业K线图
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

from tradingagents.utils.credentials import load_wrds_credentials
from tradingagents.dataflows.wrds_source import get_wrds_connection

try:
    from ntca_platform.symbols import resolve_symbol
    from ntca_platform.local_bars_db import load_range, clamp_to_ntca_window
    from ntca_platform.fetchers import fetch_cn_akshare, fetch_hk_yfinance, fetch_tw_yfinance
    from ntca_platform.config import PLATFORM_NAME, DATA_START
except ImportError:
    resolve_symbol = None
    load_range = None
    clamp_to_ntca_window = None
    fetch_cn_akshare = None
    fetch_hk_yfinance = None
    fetch_tw_yfinance = None
    PLATFORM_NAME = "NTCA Platform"
    DATA_START = "2020-01-01"


def get_wrds_data(ticker, start_date, end_date):
    """
    从WRDS获取准确的日线数据

    Returns:
        DataFrame: 包含OHLCV数据的DataFrame
    """
    print(f"[WRDS数据] 正在从WRDS获取 {ticker} 数据...")
    print(f"[WRDS数据] 日期范围: {start_date} 到 {end_date}")

    try:
        creds = load_wrds_credentials()
        if not creds:
            print(
                "[WRDS数据] 未配置凭据：请在项目 is/wrds.txt 写入 username/password，"
                "或设置环境变量 WRDS_USERNAME、WRDS_PASSWORD。"
            )
            return None
        print(f"[WRDS数据] 连接WRDS（用户: {creds['username']}）...")

        db = get_wrds_connection()
        print(f"[WRDS数据] 连接成功！")

        # 查询CRSP股票数据
        print(f"[WRDS数据] 查询CRSP数据库...")
        query = f"""
        SELECT
            a.date,
            a.prc AS close_price,  -- 收盘价
            COALESCE(a.openprc, a.prc) AS open_price,  -- 开盘价（字段兼容）
            a.askhi AS high_price, -- 最高价
            a.bidlo AS low_price,  -- 最低价
            a.vol AS volume        -- 成交量
        FROM
            crsp.dsf AS a
        INNER JOIN
            crsp.msenames AS b
            ON a.permno = b.permno
            AND a.date >= b.namedt
            AND a.date < b.nameendt
        WHERE
            b.ticker = '{ticker.upper()}'
            AND a.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY
            a.date
        """

        df = db.raw_sql(query)

        if df is None or len(df) == 0:
            print(f"[WRDS数据] 未找到数据，尝试备用查询...")
            # 备用查询：只用ticker
            query2 = f"""
            SELECT
                date,
                prc AS close_price,
                COALESCE(openprc, prc) AS open_price,
                askhi AS high_price,
                bidlo AS low_price,
                vol AS volume
            FROM
                crsp.dsf
            WHERE
                permno IN (SELECT permno FROM crsp.msenames WHERE ticker = '{ticker.upper()}')
                AND date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY
                date
            """
            df = db.raw_sql(query2)

        db.close()

        if df is None or len(df) == 0:
            print(f"[WRDS Data] Not found: {ticker} in WRDS")
            return None

        # 处理数据
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # 重命名列
        df.rename(columns={
            'close_price': 'CLOSE',
            'open_price': 'OPEN',
            'high_price': 'HIGH',
            'low_price': 'LOW',
            'volume': 'VOLUME'
        }, inplace=True)

        # 处理缺失值
        # 如果没有OPEN，用前一日CLOSE代替
        if df['OPEN'].isna().any():
            df['OPEN'] = df['OPEN'].fillna(df['CLOSE'].shift(1))
            df['OPEN'] = df['OPEN'].fillna(df['CLOSE'])  # 第一天用CLOSE

        # 如果没有HIGH/LOW，用CLOSE代替
        df['HIGH'] = df['HIGH'].fillna(df['CLOSE'])
        df['LOW'] = df['LOW'].fillna(df['CLOSE'])

        # 处理价格为负数的情况（CRSP中负数表示bid/ask均价）
        df[['CLOSE', 'OPEN', 'HIGH', 'LOW']] = df[['CLOSE', 'OPEN', 'HIGH', 'LOW']].abs()

        # 成交量转换为整数
        df['VOLUME'] = df['VOLUME'].fillna(0).astype(int)

        # 只保留有交易数据的日子
        df = df[df['VOLUME'] > 0]

        # 按日期排序
        df.sort_index(inplace=True)

        print(f"[WRDS Data] Successfully got {len(df)} trading days")
        print(f"[WRDS数据] 日期范围: {df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"[WRDS数据] 价格范围: ${df['LOW'].min():.2f} - ${df['HIGH'].max():.2f}")

        return df

    except Exception as e:
        print(f"[WRDS数据] 失败: {e}")
        return None


def get_us_yfinance_data(ticker, start_date, end_date):
    """US fallback when WRDS connection is unavailable."""
    try:
        print(f"[yfinance] 正在获取 {ticker} 数据...")
        # yfinance end is exclusive for daily bars; extend one day.
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        df = yf.download(
            ticker.upper(),
            start=start_date,
            end=end_dt.strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=False,
            progress=False,
        )
        if df is None or len(df) == 0:
            print(f"[yfinance] 未找到 {ticker} 数据")
            return None

        # Normalize columns to the same schema used by chart preparation.
        if "Open" not in df.columns:
            return None
        out = pd.DataFrame(index=df.index.copy())
        out["OPEN"] = pd.to_numeric(df["Open"], errors="coerce")
        out["HIGH"] = pd.to_numeric(df["High"], errors="coerce")
        out["LOW"] = pd.to_numeric(df["Low"], errors="coerce")
        out["CLOSE"] = pd.to_numeric(df["Close"], errors="coerce")
        out["VOLUME"] = pd.to_numeric(df.get("Volume", 0), errors="coerce").fillna(0).astype(int)
        out = out.dropna(subset=["OPEN", "HIGH", "LOW", "CLOSE"]).sort_index()
        if len(out) == 0:
            return None
        print(f"[yfinance] 成功获取 {len(out)} 条记录")
        return out
    except Exception as e:
        print(f"[yfinance] 失败: {e}")
        return None


def calculate_indicators(df):
    """
    计算技术指标（用于绘制指标线）

    Returns:
        dict: 包含各种技术指标的字典
    """
    print(f"[技术指标] 计算技术指标...")

    indicators = {}

    # 1. 移动平均线
    indicators['MA5'] = df['CLOSE'].rolling(window=5).mean().tolist()
    indicators['MA10'] = df['CLOSE'].rolling(window=10).mean().tolist()
    indicators['MA20'] = df['CLOSE'].rolling(window=20).mean().tolist()
    indicators['MA60'] = df['CLOSE'].rolling(window=60).mean().tolist()

    # 2. RSI (相对强弱指标)
    delta = df['CLOSE'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    indicators['RSI'] = rsi.tolist()
    indicators['RSI_MA6'] = rsi.rolling(window=6).mean().tolist()  # RSI的6日均线

    # 3. MACD (指数平滑异同移动平均线)
    exp12 = df['CLOSE'].ewm(span=12, adjust=False).mean()
    exp26 = df['CLOSE'].ewm(span=26, adjust=False).mean()
    macd_line = exp12 - exp26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    indicators['MACD'] = {
        'DIF': macd_line.tolist(),        # 快线
        'DEA': signal_line.tolist(),      # 慢线
        'MACD': macd_histogram.tolist()   # 柱状图
    }

    # 4. KDJ (随机指标)
    low_min = df['LOW'].rolling(window=9).min()
    high_max = df['HIGH'].rolling(window=9).max()
    rsv = 100 * ((df['CLOSE'] - low_min) / (high_max - low_min))
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d

    indicators['KDJ'] = {
        'K': k.tolist(),
        'D': d.tolist(),
        'J': j.tolist()
    }

    # 5. BOLL (布林带)
    ma20 = df['CLOSE'].rolling(window=20).mean()
    std20 = df['CLOSE'].rolling(window=20).std()
    upper_band = ma20 + (std20 * 2)
    lower_band = ma20 - (std20 * 2)

    indicators['BOLL'] = {
        'UPPER': upper_band.tolist(),
        'MIDDLE': ma20.tolist(),
        'LOWER': lower_band.tolist()
    }

    # 6. 成交量均线
    indicators['VOLUME_MA5'] = df['VOLUME'].rolling(window=5).mean().tolist()
    indicators['VOLUME_MA10'] = df['VOLUME'].rolling(window=10).mean().tolist()

    print(f"[Indicators] Calculation completed")
    print(f"[Indicators] Includes: MA, RSI, MACD, KDJ, BOLL, Volume MA")

    return indicators


def prepare_chart_data(
    df,
    indicators,
    ticker,
    market_label="US",
    data_source_label="WRDS",
    ntca_mode="wrds",
):
    """
    准备前端绘图数据（富途牛牛格式）

    Args:
        df: OHLCV DataFrame
        indicators: 技术指标
        ticker: 股票代码
        market_label: US / CN / HK
        data_source_label: WRDS / NTCA_DB / efinance / yfinance
        ntca_mode: wrds | local_db | live
    """
    print(f"[图表数据] 准备富途牛牛格式图表数据...")

    # 基础数据
    dates = df.index.strftime('%Y-%m-%d').tolist()

    # K线数据
    ohlcv = {
        'date': dates,
        'open': [round(x, 2) for x in df['OPEN'].tolist()],
        'high': [round(x, 2) for x in df['HIGH'].tolist()],
        'low': [round(x, 2) for x in df['LOW'].tolist()],
        'close': [round(x, 2) for x in df['CLOSE'].tolist()],
        'volume': [int(x) for x in df['VOLUME'].tolist()]
    }

    # 当前价格信息
    current = df['CLOSE'].iloc[-1]
    prev = df['CLOSE'].iloc[-2] if len(df) > 1 else current
    change = current - prev
    change_pct = (change / prev) * 100 if prev != 0 else 0

    # 汇总数据
    chart_data = {
        'ticker': ticker,
        'platform': PLATFORM_NAME,
        'market': market_label,
        'data_source': data_source_label,
        'ntca_mode': ntca_mode,
        'data_window_start': DATA_START,
        'data': {
            'ohlcv': ohlcv,
            'indicators': indicators,
            'summary': {
                'current': round(current, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'high': round(df['HIGH'].max(), 2),
                'low': round(df['LOW'].min(), 2),
                'volume': int(df['VOLUME'].iloc[-1]),
                'datetime': df.index[-1].strftime('%Y-%m-%d')
            }
        }
    }

    print(f"[Chart Data] Preparation completed")
    print(f"[图表数据] 当前价格: ${current:.2f} ({change:+.2f}, {change_pct:+.2f}%)")

    return chart_data


def get_wrds_chart_data(ticker, start_date, end_date, market_type="us"):
    """
    NTCA：优先实时数据源，失败则回退本地库（2020-01-01 至今）。

    - 美股：WRDS -> 本地 SQLite
    - A 股：AkShare -> 本地库
    - 港股 / 台股：yfinance (Ticker) -> 本地库

    Args:
        ticker: 股票代码或中文名（见 ntca_platform.symbols）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        market_type: us | cn | hk | tw
        WRDS 凭据仅从 is/wrds.txt（或环境变量）读取。
    """
    print("=" * 80)
    print(f"{PLATFORM_NAME} — chart pipeline")
    print("=" * 80)
    print()

    mt = (market_type or "us").lower()
    if resolve_symbol is None or load_range is None:
        df = get_wrds_data(ticker, start_date, end_date)
        if df is None or len(df) == 0:
            print("[错误] 无法获取数据（NTCA 模块未加载）")
            return None
        indicators = calculate_indicators(df)
        return prepare_chart_data(df, indicators, ticker, "US", "WRDS", "wrds")

    resolved = resolve_symbol(ticker, mt)
    if not resolved:
        print("[错误] 无法解析股票代码")
        return None

    s, e = clamp_to_ntca_window(start_date, end_date)
    df = None
    src_label = "WRDS"
    mode = "wrds"
    mkt = "US"

    if mt == "us":
        mkt = "US"
        # 优先本地 SQLite（prefetch_ntca.py 预取），减少每次现查 WRDS；不足再拉 WRDS
        df_local = load_range(resolved, s, e)
        if df_local is not None and len(df_local) >= 5:
            df = df_local
            src_label = "NTCA_DB"
            mode = "local_db"
        else:
            df = get_wrds_data(resolved, s, e)
            if df is not None and len(df) > 0:
                src_label = "WRDS"
                mode = "wrds"
            else:
                # WRDS 网络不通时，自动回退到 yfinance，避免图表完全失败
                df = get_us_yfinance_data(resolved, s, e)
                if df is not None and len(df) > 0:
                    src_label = "yfinance"
                    mode = "live"
                else:
                    df = df_local
                if df is not None and len(df) > 0:
                    src_label = "NTCA_DB"
                    mode = "local_db"
                else:
                    df = None

    elif mt == "cn":
        mkt = "CN"
        df = fetch_cn_akshare(resolved, s, e)
        if df is not None and len(df) > 0:
            src_label = "akshare"
            mode = "live"
        else:
            df = load_range(resolved, s, e)
            src_label = "NTCA_DB"
            mode = "local_db"

    elif mt == "hk":
        mkt = "HK"
        df = fetch_hk_yfinance(resolved, s, e)
        if df is not None and len(df) > 0:
            src_label = "yfinance"
            mode = "live"
        else:
            df = load_range(resolved, s, e)
            src_label = "NTCA_DB"
            mode = "local_db"

    elif mt == "tw":
        mkt = "TW"
        df = fetch_tw_yfinance(resolved, s, e)
        if df is not None and len(df) > 0:
            src_label = "yfinance"
            mode = "live"
        else:
            df = load_range(resolved, s, e)
            src_label = "NTCA_DB"
            mode = "local_db"

    else:
        df = get_wrds_data(resolved, s, e)
        mkt = "US"
        if df is None or len(df) == 0:
            df = load_range(resolved, s, e)
            src_label = "NTCA_DB"
            mode = "local_db"
        else:
            src_label = "WRDS"
            mode = "wrds"

    if df is None or len(df) == 0:
        print("[错误] 无法获取数据（请运行 python prefetch_ntca.py 预取本地库）")
        return None

    indicators = calculate_indicators(df)
    chart_data = prepare_chart_data(
        df, indicators, resolved, mkt, src_label, mode
    )

    print()
    print("=" * 80)
    print(f"[OK] 图表数据准备完成！数据点: {len(df)}  | 模式: {mode} | 来源: {src_label}")
    print("=" * 80)

    return chart_data


if __name__ == "__main__":
    # 测试
    import json
    result = get_wrds_chart_data("AAPL", "2024-06-01", "2024-08-15")

    if result:
        print("\n" + "="*80)
        print("数据预览:")
        print(f"股票代码: {result['ticker']}")
        print(f"当前价格: ${result['data']['summary']['current']}")
        print(f"涨跌: {result['data']['summary']['change']:.2f} ({result['data']['summary']['change_pct']:.2f}%)")
        print(f"数据点: {len(result['data']['ohlcv']['date'])}")
        print(f"指标数量: {len(result['data']['indicators'])}")
        print("="*80)

        # 保存到文件测试
        with open('chart_data_test.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\n已保存到: chart_data_test.json")
