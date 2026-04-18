"""
ACCE v2.0 - 快速配置
针对Web界面优化的高性能配置
"""

import os

FAST_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),

    # ===== LLM 设置 - 优化版 =====
    "llm_provider": "openai",
    "backend_url": "https://api.deepseek.com/v1",  # 使用DeepSeek（最快）

    # 使用快速模型
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",

    # Provider-specific thinking configuration
    "google_thinking_level": "minimal",      # 使用最小思考级别
    "openai_reasoning_effort": "low",       # 低推理努力
    "anthropic_effort": "low",              # 低努力级别

    # 输出语言
    "output_language": "Chinese",

    # 满血默认（可用环境变量或副本覆盖为快速演示）
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3,
    "max_recur_limit": 200,

    # 并行化设置
    "enable_parallel_agents": True,   # 启用并行智能体处理
    "max_parallel_workers": 3,        # 最多3个并行AI请求

    # 数据供应商配置 - 使用最快的API
    "data_vendors": {
        "core_stock_apis": "wrds",          # WRDS对于历史数据最快
        "technical_indicators": "wrds",
        "fundamental_data": "wrds",
        "news_data": "yfinance",            # 新闻数据用yfinance
    },

    # 工具级配置
    "tool_vendors": {},

    # 缓存设置
    "enable_data_cache": True,        # 启用数据缓存
    "cache_ttl_hours": 24,            # 缓存24小时
}

# ===== 预设配置文件 =====

# 超快速模式 - 适合演示
ULTRA_FAST_CONFIG = FAST_CONFIG.copy()
ULTRA_FAST_CONFIG.update({
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 80,
    "openai_reasoning_effort": "low",
})

# 平衡模式 - 速度和质量平衡
BALANCED_CONFIG = FAST_CONFIG.copy()
BALANCED_CONFIG.update({
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 150,
})

# 深度模式 - 质量优先（原有配置）
DEEP_CONFIG = FAST_CONFIG.copy()
DEEP_CONFIG.update({
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3,
    "max_recur_limit": 200,
})
