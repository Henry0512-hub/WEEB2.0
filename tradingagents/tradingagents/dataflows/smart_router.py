"""
智能数据源路由器
根据资产代码自动选择最佳数据源（支持股票、A股、加密货币）
"""

from .efinance_source import is_a_share_stock
from .coingecko_source import is_cryptocurrency


def get_smart_config(ticker: str, base_config: dict) -> dict:
    """
    根据资产代码智能配置数据源

    Args:
        ticker: 资产代码（股票或加密货币）
        base_config: 基础配置

    Returns:
        dict: 更新后的配置
    """
    config = base_config.copy()

    # 优先检测是否为加密货币
    if is_cryptocurrency(ticker):
        print(f"[INFO] Crypto ticker '{ticker}' -> CoinGecko")

        # 为加密货币设置coingecko为首选数据源
        if "data_vendors" not in config:
            config["data_vendors"] = {}

        config["data_vendors"]["core_stock_apis"] = "coingecko"
        config["data_vendors"]["fundamental_data"] = "coingecko"

        # 技术指标和新闻使用yfinance作为fallback
        config["data_vendors"]["technical_indicators"] = "yfinance"
        config["data_vendors"]["news_data"] = "yfinance"

        # 工具级别配置
        if "tool_vendors" not in config:
            config["tool_vendors"] = {}

        config["tool_vendors"]["get_stock_data"] = "coingecko,yfinance"
        config["tool_vendors"]["get_fundamentals"] = "coingecko,yfinance"

    # 检测是否为A股
    elif is_a_share_stock(ticker):
        print(f"[INFO] A-share '{ticker}' -> EFinance")

        # 为A股设置efinance为首选数据源
        if "data_vendors" not in config:
            config["data_vendors"] = {}

        config["data_vendors"]["core_stock_apis"] = "efinance"
        config["data_vendors"]["fundamental_data"] = "efinance"

        # 其他数据源使用yfinance作为fallback
        config["data_vendors"]["technical_indicators"] = "yfinance"
        config["data_vendors"]["news_data"] = "yfinance"

        # 工具级别配置
        if "tool_vendors" not in config:
            config["tool_vendors"] = {}

        config["tool_vendors"]["get_stock_data"] = "efinance,yfinance"
        config["tool_vendors"]["get_fundamentals"] = "efinance,yfinance"

    else:
        dv = config.get("data_vendors") or {}
        core = dv.get("core_stock_apis", "yfinance")
        fund = dv.get("fundamental_data", "yfinance")
        if core == "wrds":
            print(f"[INFO] '{ticker}': OHLC=WRDS (coursework academic route); fundamentals={fund} (non-WRDS)")
        else:
            print(f"[INFO] '{ticker}': OHLC vendor={core}; fundamentals vendor={fund}")

    return config
