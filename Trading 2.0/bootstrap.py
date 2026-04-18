"""
Trading 2.0 — 可选运行时补丁（不修改上级目录源文件）。

默认：不施加任何限制（与主程序一致，含加密货币路由）。
仅当设置环境变量 TRADING20_NO_CRYPTO=1 时，才拦截加密货币标的。
"""


def apply_no_crypto_patch() -> None:
    import os

    if os.environ.get("TRADING20_NO_CRYPTO", "").strip().lower() not in ("1", "true", "yes", "on"):
        return

    import functools
    import tradingagents.dataflows.smart_router as smart_router
    import tradingagents.dataflows.coingecko_source as cg

    _orig_is_crypto = cg.is_cryptocurrency
    _orig_get_smart = smart_router.get_smart_config

    @functools.wraps(_orig_get_smart)
    def get_smart_config_no_crypto(ticker: str, base_config: dict) -> dict:
        if _orig_is_crypto(ticker):
            raise ValueError(
                "Trading 2.0（TRADING20_NO_CRYPTO=1）：本模式不包含加密货币。"
                "请使用美股、港股或 A 股代码。"
            )
        return _orig_get_smart(ticker, base_config)

    smart_router.get_smart_config = get_smart_config_no_crypto
