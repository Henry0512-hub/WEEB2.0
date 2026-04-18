from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)


def get_language_instruction() -> str:
    """Return a prompt instruction for the configured output language.

    Returns empty string when English (default), so no extra tokens are used.
    Only applied to user-facing agents (analysts, portfolio manager).
    Internal debate agents stay in English for reasoning quality.
    """
    from tradingagents.dataflows.config import get_config
    lang = get_config().get("output_language", "English")
    if lang.strip().lower() == "english":
        return ""
    return f" Write your entire response in {lang}."


def _is_chinese_output() -> bool:
    from tradingagents.dataflows.config import get_config

    lang = (get_config().get("output_language") or "English").strip().lower()
    return lang in ("chinese", "中文", "zh", "zh-cn", "cn", "mandarin")


def get_professional_metrics_instruction(variant: str = "full") -> str:
    """Prompt block so final reports cite profitability, liquidity, leverage, and beta.

    Args:
        variant: ``full`` for fundamentals / portfolio synthesis; ``brief`` for debators/trader.
    """
    zh = _is_chinese_output()

    if variant == "brief":
        if zh:
            return (
                " 论证时请引用基本面中的具体数值或区间（如毛利率、P/E、流动比率、债务权益比、β 等），并说明其对结论的影响。"
            )
        return (
            " Cite concrete fundamentals (e.g. gross margin, P/E, current ratio, D/E, β) and explain how each affects your conclusion."
        )

    if zh:
        return (
            "\n\n【专业财务指标要求】在报告与最终结论中须用数据体现专业性；若工具或数据中可得，请显式讨论并尽量给出数值：\n"
            "· 盈利能力：毛利率、营业利润率、净利率、ROE、ROA；回报口径可用 ROE/ROA 或现金流回报说明（与 ROI 同向解读）。\n"
            "· 估值：市盈率（P/E TTM/前瞻）、PEG、市净率（P/B）。\n"
            "· 流动性：流动比率（Current Ratio）、速动比率（Quick Ratio）；若仅有报表科目请简述推算逻辑。\n"
            "· 杠杆与风险：债务权益比（Debt/Equity，常作 gearing）、资产负债率；利息保障倍数（若有）。\n"
            "· 系统性风险：数据源中的 Beta 通常为权益 β（Equity Beta）；若讨论资产 β（Asset Beta）须说明去杠杆/资本结构假设。\n"
            "请设「关键指标小结」小节，用 Markdown 表格列出上述可得指标，并逐条解释其对投资含义。"
        )

    return (
        "\n\n**Professional metrics (required in the report where data permits):** "
        "Profitability: gross margin, operating margin, net margin, ROE, ROA; tie “ROI-style” ideas to ROE/ROA or cash-based returns. "
        "Valuation: P/E (TTM/forward), PEG, P/B. "
        "Liquidity: current ratio, quick ratio (derive from line items if needed). "
        "Leverage: debt-to-equity (gearing), debt ratios, interest coverage if available. "
        "Risk: equity β (vendor “Beta”); if discussing asset β, state unlevering assumptions. "
        "Add a **Key metrics** subsection with a Markdown table and link each figure to your investment conclusion."
    )


def get_data_grounding_instruction() -> str:
    """Require reports to cite only numbers present in tool outputs; forbid invented figures."""
    if _is_chinese_output():
        return (
            "\n\n【数据真实性约束】最终报告、技术分析与财务分析只能使用本次任务中工具返回、"
            "行情/图表接口已给出的数字与指标序列；禁止编造未出现在上述输出中的具体价格、"
            "RSI、均线、成交量、财务比率等。若某项未获取，须明确写「数据未在工具/本地结果中提供」，"
            "不得用常识或训练记忆填补。段落中引用的每一个关键数字应能在工具原始输出或 CSV 中对上。"
        )
    return (
        "\n\n**Data grounding:** Final reports must use only numbers and series that appear in tool outputs "
        "or the retrieved market/fundamental data for this run. Do not invent prices, RSI, moving averages, "
        "volume, or financial ratios that are not explicitly present. If a figure is missing, write "
        "“not provided in tool output” rather than guessing."
    )


def build_instrument_context(ticker: str) -> str:
    """Describe the exact instrument so agents preserve exchange-qualified tickers."""
    return (
        f"The instrument to analyze is `{ticker}`. "
        "Use this exact ticker in every tool call, report, and recommendation, "
        "preserving any exchange suffix (e.g. `.TO`, `.L`, `.HK`, `.T`)."
    )

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        
