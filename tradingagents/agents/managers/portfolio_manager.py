from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_data_grounding_instruction,
    get_language_instruction,
    get_professional_metrics_instruction,
    _is_chinese_output,
    is_homework_simple_mode,
)


def create_portfolio_manager(llm, memory):
    def portfolio_manager_node(state) -> dict:

        instrument_context = build_instrument_context(state["company_of_interest"])

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        research_plan = state["investment_plan"]
        trader_plan = state["trader_investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        if _is_chinese_output():
            if is_homework_simple_mode():
                structure = """**作业版输出结构（中文，约 550–950 字；要有实质分析，但不要写成卖方长篇研报）：**
1. **核心观点**：开头写明评级（Buy / Overweight / Hold / Underweight / Sell 之一），再用 2–4 句话概括依据（可引用前序分析师结论中的要点）。
2. **基本面与财务分析**：**必须有实质内容**：简述公司做什么、所在行业/景气度一句话；并结合工具数据写 **至少两类** 财务维度（盈利/成长、估值、杠杆或流动性中的两类），每类带 1–2 个数字或比率；缺失写「数据未提供」。可用短段落或小列表，不要冗长大表。
3. **技术分析（含布林带超买超卖）**：**必须讨论布林带**：根据工具/前序分析中的上轨、中轨、下轨（或 boll_ub / boll / boll_lb）说明当前价格相对位置——是否贴近/触及上轨（偏超买）、贴近/触及下轨（偏超卖）、沿中轨整理或带宽收窄等；**要用到的数值须来自本次任务输出**，不可臆造；若整条布林带未获取则明确写「布林带数据未提供」，并仅用已有指标略写趋势。
4. **风险与投资建议**：列出 **2 条**主要风险（各一句话）；再给一句可执行建议（仓位倾向、止损/观察价有数据则写）。

格式：使用上述 **四个** 小节标题；数字与结论须能在工具或分析师材料中对上。"""
            else:
                structure = """**Required Output Structure (must follow exactly, in Chinese, ~1000 Chinese characters):**
1. **核心观点**：用 1-2 句话明确给出总判断，并先写出评级（Buy / Overweight / Hold / Underweight / Sell 之一）。
2. **基本面简述**：简述公司主营业务、行业景气度、竞争位置，并引用可得财务指标（如盈利能力、估值、流动性、杠杆、β）。
3. **技术分析（重点）**：围绕价格趋势、均线结构、动量/波动指标与关键支撑阻力位，说明当前买卖时机逻辑。
4. **风险提示**：至少列出 3 条主要风险（如业绩不及预期、估值回撤、宏观/利率、流动性、事件冲击），并说明触发条件。
5. **投资建议**：给出明确可执行建议（仓位区间、分批/一次性、止损位、止盈位、观察期限）。

Formatting constraints:
- 总长度控制在约 900-1100 个中文字符；
- 标题必须使用上述 5 个小节名称；
- 所有关键数字必须来自本次工具输出；缺失则标注“数据未提供”。"""
        else:
            if is_homework_simple_mode():
                structure = """**Coursework-style structure (English, about 380–620 words—substantive but not a sell-side memo):**
1. **Core View**: **Rating first** (exactly one of Buy / Overweight / Hold / Underweight / Sell), then 2–4 sentences tying to evidence from the workflow.
2. **Fundamentals & Financial Analysis**: **Required substance**: one line on what the company does and industry context; then cover **at least two of** profitability/growth, valuation (e.g. P/E, P/B if available), leverage/liquidity—each with 1–2 numbers from tools. Short bullets/paragraphs OK; no huge tables. If a dimension is missing, say **Data not provided.**
3. **Technical Analysis (Bollinger overbought/oversold)**: **Must discuss Bollinger Bands** using upper/middle/lower (or `boll_ub` / `boll` / `boll_lb`) from this run: e.g. price hugging upper band (overbought stretch), lower band (oversold), riding the middle, or squeeze. **Use only tool-reported values**; if bands were not retrieved, state **Bollinger data not provided** and briefly use whatever technicals exist.
4. **Risks & Investment Recommendation**: **Two** one-line risks, then one actionable recommendation (sizing/stop/watch level only if supported by data).

Use exactly these **four** Markdown headings; every number must trace to tool/analyst outputs."""
            else:
                structure = """**Required Output Structure (must follow exactly, in English, ~600–900 words):**
1. **Core View**: In 1–2 sentences state the overall judgment and **lead with the rating** (exactly one of Buy / Overweight / Hold / Underweight / Sell).
2. **Fundamentals**: Brief business model, industry cycle, competitive position; cite available metrics (profitability, valuation, liquidity, leverage, β).
3. **Technical Analysis (focus)**: Trend, moving-average structure, momentum/volatility vs. key support/resistance; timing logic for entries/exits.
4. **Risk Factors**: At least three material risks (e.g. earnings miss, multiple compression, macro/rates, liquidity, idiosyncratic events) with **trigger conditions**.
5. **Investment Recommendation**: Actionable guidance (position sizing range, scale-in vs. lump-sum, stop-loss, take-profit, review horizon).

Formatting constraints:
- Use **exactly** the five section titles above as Markdown headings;
- Every number must come from this run’s tool outputs; if missing, write **“Data not provided.”**"""

        prompt = f"""As the Portfolio Manager, synthesize the risk analysts' debate and deliver the final trading decision.

{instrument_context}

---

**Rating Scale** (use exactly one):
- **Buy**: Strong conviction to enter or add to position
- **Overweight**: Favorable outlook, gradually increase exposure
- **Hold**: Maintain current position, no action needed
- **Underweight**: Reduce exposure, take partial profits
- **Sell**: Exit position or avoid entry

**Context:**
- Research Manager's investment plan: **{research_plan}**
- Trader's transaction proposal: **{trader_plan}**
- Lessons from past decisions: **{past_memory_str}**

{structure}

---

**Risk Analysts Debate History:**
{history}

---

Be decisive and ground conclusions in the analysts’ evidence.{get_professional_metrics_instruction("full")}{get_data_grounding_instruction()}{get_language_instruction()}{" Balance depth with brevity: meet every coursework bullet (fundamentals + Bollinger) without writing an institutional equity research report." if is_homework_simple_mode() else ""}"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return portfolio_manager_node
