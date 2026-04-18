from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_data_grounding_instruction,
    get_language_instruction,
    get_professional_metrics_instruction,
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

**Required Output Structure (must follow exactly, Chinese only, ~1000 Chinese characters):**
1. **核心观点**：用 1-2 句话明确给出总判断，并先写出评级（Buy / Overweight / Hold / Underweight / Sell 之一）。
2. **基本面简述**：简述公司主营业务、行业景气度、竞争位置，并引用可得财务指标（如盈利能力、估值、流动性、杠杆、β）。
3. **技术分析（重点）**：围绕价格趋势、均线结构、动量/波动指标与关键支撑阻力位，说明当前买卖时机逻辑。
4. **风险提示**：至少列出 3 条主要风险（如业绩不及预期、估值回撤、宏观/利率、流动性、事件冲击），并说明触发条件。
5. **投资建议**：给出明确可执行建议（仓位区间、分批/一次性、止损位、止盈位、观察期限）。

Formatting constraints:
- 总长度控制在约 900-1100 个中文字符；
- 标题必须使用上述 5 个小节名称；
- 所有关键数字必须来自本次工具输出；缺失则标注“数据未提供”。

---

**Risk Analysts Debate History:**
{history}

---

Be decisive and ground every conclusion in specific evidence from the analysts.{get_professional_metrics_instruction("full")}{get_data_grounding_instruction()}{get_language_instruction()}"""

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
