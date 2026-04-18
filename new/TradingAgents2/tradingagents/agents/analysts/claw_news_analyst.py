"""
Claw 新闻分析师 - 使用 crawl4ai 爬取中国新闻

这是 TradingAgents 的一个额外的新闻分析师，
专门用于获取中国本土新闻源的实时数据。
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_language_instruction,
)
from tradingagents.dataflows.config import get_config


def get_claw_chinese_news(query: str = "", limit: int = 10) -> str:
    """
    使用 Claw 爬虫获取中国新闻

    Args:
        query: 查询关键词（可选）
        limit: 新闻数量限制

    Returns:
        格式化的新闻字符串
    """
    try:
        from claw_news_crawler import crawl_chinese_news_sync

        news = crawl_chinese_news_sync(limit_per_source=limit)

        if query:
            # 如果有查询词，简单过滤
            if query.lower() in news.lower():
                return news
            else:
                return f"未找到关于 '{query}' 的相关中国新闻"

        return news

    except Exception as e:
        return f"Claw 爬虫获取新闻失败: {str(e)}"


def create_claw_news_analyst(llm):
    """
    创建 Claw 新闻分析师节点

    这个分析师专门使用 Claw 爬虫获取中国财经新闻，
    补充原有的 yfinance 和 Alpha Vantage 新闻源。

    Args:
        llm: 语言模型实例

    Returns:
        分析师节点函数
    """
    def claw_news_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        # Claw 新闻工具
        tools = [
            get_claw_chinese_news,
        ]

        system_message = (
            "你是一个专门分析中国财经新闻的研究员。你的任务是从中国本土新闻源（央视网、新浪财经、东方财富等）"
            "获取最新的财经新闻和市场动态，为交易决策提供中国市场的独特视角。\n\n"
            "你可以使用的工具：get_claw_chinese_news(query, limit) - 爬取中国财经新闻\n\n"
            "分析重点：\n"
            "1. 中国宏观经济政策（央行政策、财政政策等）\n"
            "2. A 股市场动态和监管变化\n"
            "3. 中国企业（特别是分析目标公司）的相关新闻\n"
            "4. 中美关系、贸易政策对市场的影响\n"
            "5. 人民币汇率、外汇储备等信息\n\n"
            "请提供具体、可操作的见解，并附上支持证据。"
            """ 报告末尾请附加 Markdown 表格，汇总报告中的关键要点，便于阅读。"""
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个乐于助人的 AI 助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你无法完全回答，没关系；另一个具有不同工具的助手"
                    " 会在你停下的地方继续帮助。执行你能做的来取得进展。"
                    " 如果你或任何其他助手有最终交易提案：**买入/持有/卖出** 或可交付成果，"
                    " 请在回复前加上 FINAL TRANSACTION PROPOSAL: **买入/持有/卖出**，以便团队知道停止。"
                    " 你可以访问以下工具: {tool_names}.\n{system_message}"
                    "参考日期: {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "claw_news_report": report,  # 使用独立的报告字段
        }

    return claw_news_analyst_node
