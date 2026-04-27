
#WERITE in the front
very quick start
step1 download zip
step2 open is 
step3 create a new txt input your wrds user and password like this
username: henghye24
password: BHGHugyyu#
(that is an example,and totally fake,just input in such mode)
step4 save the txt search for 启动ACCE Web
step5 double click it.
step6 you can use it
Remender: all apis only have the login gift money and can not use too much and if you want to use it please go into is/api assents to change those into yours own keys. Also I sincerely recommand deepseek and Kimi to analysis for the genimi is not stable enough.




# TradingAgents - ACCE v2.0 (AI Trading Analysis Platform)

**Quick start (Windows, no garbled console):** double-click **`QUICKSTART.bat`** in the folder that contains `web_backend.py`, then open **http://localhost:5000**. Details: **`QUICKSTART.md`**.

**A comprehensive local-first multi-agent AI system for stock, A-share, and crypto analysis.**

This project combines:
- **8 specialized AI agents** orchestrated via LangGraph
- **Intelligent multi-source data fetching** (WRDS academic data, akshare, efinance, Alpha Vantage, CoinGecko)
- **LLM-powered report generation** (DeepSeek recommended, Kimi, Gemini)
- **Modern web UI** in an **industrial steam-age workshop** look (brass, cast iron, parchment, coal-smoke tones) with real-time candlestick charts + MA indicators
- **News analysis** with Claw crawler and sentiment tools
- **CLI tools, tests, prefetchers, and notebooks**

**Project for educational/research purposes (ACC102 Track 4 - Interactive Tool). Not financial advice.**

**Author**: Heng.Yang (Student No. 2469312)  
**Last Updated**: 2026-04-18  
**Status**: ✅ Production-ready web interface with full agent system
However, as a educational edition only US equality based on wrds is useful and the whole app is going to be released in 2026

---

## ✨ Key Features

### Core AI System
- **8-Agent Collaboration**:
  1. **Market Analyst** - Technical analysis, price trends, indicators
  2. **News/Social Analyst** - Sentiment from news, social media, Claw crawler
  3. **Fundamentals Analyst** - Balance sheets, income statements, cash flow
  4. **Bull Researcher** - Optimistic arguments with memory
  5. **Bear Researcher** - Risk-focused counterarguments with memory
  6. **Risk Debators** (Aggressive, Conservative, Neutral) - Debate investment risks
  7. **Trader** - Synthesizes into trading plan
  8. **Portfolio Manager** - Final decision, rating (Strong Buy/Buy/Hold/Sell), target price
- **Memory & Reflection**: Agents learn from past decisions using `FinancialSituationMemory`
- **LangGraph Orchestration**: Conditional logic for debate rounds, state propagation, signal processing
- **State Logging**: Full agent states saved as JSON per ticker/date (`results/{ticker}/TradingAgentsStrategy_logs/`)

### Data Intelligence
- **Smart Router** (`tradingagents/dataflows/smart_router.py`):
  - **Crypto**: CoinGecko primary
  - **A-shares (CN)**: efinance/akshare primary
  - **US Stocks**: WRDS (historical ≤2024-12-31 for academic data), akshare/Alpha Vantage fallback for recent data
- **Prefetch & Caching**: `ntca_platform/`, `prefetch_*`, local bars DB
- **Tools**: Technical indicators (MA, RSI, Bollinger, MACD via stockstats), fundamentals, news, insider transactions, global news
- **News Analysis**: Dedicated `claw_news_crawler.py`, `run_with_claw_analyst.py`, `tradingagents/agents/analysts/claw_news_analyst.py`

### Interfaces
1. **Web UI** (`web_backend.py` + `templates/index.html`): 
   - **Industrial Revolution / steam-era** visual language: soot-and-wood dark base, **brass & copper** accents, **parchment** text, subtle riveted-plate and workshop grid overlays (`static/industrial.css`)
   - Real-time **candlestick K-line charts** with Chart.js + financial plugin, MA5/MA20/MA50 lines
   - WebSocket live progress, chart updates, report streaming
   - Model/market/symbol/date/language selection (zh/en reports)
   - One-click "开始分析"
2. **CLI Integrated** (`run_integrated_analysis.py`, `run_analysis_web.py`): Interactive prompts, full agent run
3. **Specialized Scripts**: `run_news_analysis.py`, `run_crypto_trading.py`, `run_with_deepseek.py`, etc.
4. **Notebooks**: Analytical workflows in `notebooks/`

### LLM Factory
- `tradingagents/llm_clients/`: Factory supporting OpenAI-compatible (DeepSeek, Kimi), Google (Gemini), Anthropic
- Configurable thinking levels, timeouts, retries, reasoning effort
- `deepseek_config.py`, credential loading from files/env (`tradingagents/utils/credentials.py`)

### Testing & Diagnostics
- Comprehensive test suite (`test_*.py`, `new/test_*.py`)
- WRDS diagnostics (`wrds_diagnostic.py`, `test_wrds*.py`)
- API key validation, crypto diagnosis, A-share tests
- Data science libs test, network test, full flow test

---

## 🚀 Quick Start (Web UI - Recommended)

### 1. Prerequisites
- Windows 10/11 (optimized launchers)
- Python 3.11+ (3.13 tested)
- Git cloned to `C:\Users\lenovo\TradingAgents`

### 2. Configure Credentials

**Recommended locations** (utils auto-detect multiple formats):

**LLM APIs** (`is/api assents.txt` or `new/api assents.txt`):
```text
deepseek: sk-your-deepseek-key
kimi: sk-your-kimi-key
gemini: AIzaSy-your-gemini-key
```

**WRDS** (`is/wrds.txt` or `id.txt` or root):
```text
username: your_wrds_username
password: your_wrds_password
```

**Alpha Vantage** (`av api.txt`):
```
YOUR_ALPHA_VANTAGE_KEY
```

**Alternative**: Use `api_config.py`, env vars (`DEEPSEEK_API_KEY`, etc.), or run setup scripts.

Run tests:
```bash
cd new
python test_all_apis.py
python test_api_keys.py
```

### 3. Launch Web App (Recommended)

**Easiest**:
- Double-click `启动ACCE_Web.bat` (or `new/acce_v2.0.01_Integrated.bat`)
- Or run:
```bash
pip install -r web_requirements.txt
python -X utf8 web_backend.py
```

**Access**: http://localhost:5000 (or LAN IP:5000)

**Desktop shortcut**: Use `创建快捷方式.py` or `create_shortcut.vbs`

### 4. Usage in Web UI
1. **Select Model**: DeepSeek (recommended, cost-effective), Kimi, or Gemini
2. **Market**: US, HK, CN (A-shares), Crypto (partial)
3. **Symbol**: `AAPL`, `TSLA`, `000001` (Ping An Bank), `600519.SS` (Kweichow Moutai), `BTC` 
4. **Date Range**: Note WRDS cutoff (~2024-12-31 for historical academic data)
5. **Language**: 中文 or English
6. Click **开始分析**
7. Watch:
   - Live chart data loading (OHLC + MAs)
   - Real-time agent messages via WebSocket
   - Final structured report grouped by agent
   - Investment recommendation with rationale and risks

**Expected Analysis Time**: 3-10 minutes depending on model and complexity.

**Common Test Case**: DeepSeek + US + AAPL + last 1-3 months + 中文

---

## 📁 Project Structure

```
TradingAgents/
├── web_backend.py              # Flask + Flask-Sock backend, WS parsing for charts/reports
├── run_analysis_web.py         # Core analysis runner called by web (UTF8, smart config)
├── run_integrated_analysis.py  # Interactive CLI with full agents
├── templates/index.html        # Steam-age industrial UI, Chart.js candlestick, WS client
├── static/industrial.css       # Brass / iron / parchment workshop theme (inline tool available)
├── 启动ACCE_Web.bat            # One-click Windows launcher
├── tradingagents/              # Core package
│   ├── agents/                 # 8 AI agents + managers (bull/bear, debators, trader, portfolio)
│   ├── dataflows/              # Smart router, sources (wrds, akshare, efinance, coingecko, alpha_vantage)
│   ├── graph/                  # LangGraph setup, conditional logic, reflection, propagation
│   ├── llm_clients/            # Factory + clients for DeepSeek/Kimi/Gemini/etc.
│   └── utils/                  # Credentials, tools, signals, memory
├── ntca_platform/              # Data prefetch, local DB, symbols
├── new/                        # Additional guides, tests, launchers, summaries
├── results/                    # Analysis outputs, charts, JSON state logs
├── notebooks/                  # Jupyter workflows
├── tests/ & test_*.py          # Extensive validation suite
├── requirements*.txt           # Deps (web, track4)
└── *.md                        # Docs, summaries, troubleshooting
```

Key modules:
- `tradingagents/default_config.py`: Base settings (LLM models, debate rounds, dirs)
- `tradingagents/dataflows/interface.py & smart_router.py`: Unified data access
- `tradingagents/graph/trading_graph.py`: Main orchestration class

---

## 🛠️ Advanced Usage

### CLI Integrated Analysis
```bash
python run_integrated_analysis.py
# Follow interactive prompts for model, ticker, dates, analysis type
```

Or direct:
```bash
python run_analysis_web.py --ticker AAPL --start 2023-01-01 --end 2023-12-31 --model deepseek
```

### News-Focused Analysis
```bash
python run_with_claw_analyst.py
python run_news_analysis.py
```

### Crypto
```bash
python run_crypto_trading.py
python check_crypto_support.py
python diagnose_crypto.py
# Note: Crypto support is maturing (CoinGecko integration)
```

### WRDS & Data Priority
- Use `wrds_connection_fixed.py`, `setup_wrds_pgpass.py`, `wrds_auto_connect.py`
- Historical academic data prioritized via date-based routing in `run_analysis_web.py`
- Prefetch scripts for performance (`prefetch_ntca.py`, `prefetch_user_multi_source.py`)

### Testing Everything
```bash
python new/test_system.py
python test_full_flow.py
python test_wrds_priority.py
python test_current_models.py
```

See `TROUBLESHOOTING.md`, `QUICK_REFERENCE.md`, `new/*.md` for details.

---

## ⚙️ Configuration Details

### LLM Models (from `model_catalog.py`)
- **DeepSeek**: Fast, cost-effective (~¥1/M tokens), excellent for Chinese/English
- **Kimi**: Strong 128k context, Chinese optimized
- **Gemini**: Free tier (1500 req/day), good multimodal

Configure via:
1. Credential files (parsed by `credentials.py`)
2. `deepseek_config.py` / `api_config.py`
3. Environment variables
4. Web UI dropdown

### Data Cutoffs & Fallbacks
- WRDS: Best for data ≤ ~2024/2025 (academic access required)
- Post-cutoff or A-shares: akshare/efinance
- Fallbacks: Alpha Vantage, yfinance (with network considerations in CN)
- Smart detection for ticker type (stock vs A-share vs crypto)

### Environment
- `web_requirements.txt` for Flask + WS
- Full deps in `requirements_track4.txt`
- UTF-8 handling critical on Windows (`-X utf8`)

---

## 🎨 Web UI Details

- **Design**: **Industrial steam-age trading floor** — deep soot/wood backgrounds, brass and copper trim, parchment-like panels, soft gas-lamp warmth, and machined grid texture (not neon cyberpunk). Typography leans **serif display + readable body** for a ledger/workshop feel.
- **Charts**: True candlestick (`type: 'candlestick'`), overlaid MA lines (contrasting against the dark industrial canvas), responsive
- **Workflow Visualization**: Agent nodes styled as part of the same brass-and-iron instrument panel
- **Live Updates**: WebSocket streams agent outputs, price data (parsed CSV OHLC), progress
- **Report Parsing**: Filters noise (JSON, warnings, tool calls), keeps agent insights, recommendations, CSV data for charts
- **Persistence**: Auto-reload templates, no-cache for dev

See `PROJECT_MEMORY.md`, `new/ACCE性能优化报告.md`, `tools/inline_industrial_css.py` for implementation notes.

---

## 📊 Example Outputs
- **Charts**: `results/AAPL_analysis.png`, interactive in web
- **Reports**: Structured per-agent + final trade decision (buy/hold/sell with confidence)
- **Data**: `results/{ticker}_data.csv`, full state JSON logs
- **News**: Sentiment scores, key articles from Claw/global sources

Typical recommendation includes:
- Technical summary (trend, indicators)
- Fundamental health
- News/sentiment
- Bull vs Bear debate summary
- Risk assessment
- Final **investment plan** with target price and rationale

---

## 🔧 Troubleshooting & Common Issues

**See dedicated files**:
- `TROUBLESHOOTING.md`
- `new/WRDS_CONNECTION_FIX.md`
- `new/系统最终完成报告.md`
- `QUICK_REFERENCE.md`
- `API_CONFIG_GUIDE.md`

**Frequent Fixes**:
1. **Credential not found**: Check `is/`, `new/`, root files; restart after changes
2. **Chart shows wrong/no data**: Ensure OHLC CSV not filtered in `web_backend.py` parser; correct ticker
3. **WRDS fails**: Run `test_wrds.py` or `wrds_diagnostic.py`; check VPN/academic access; use `setup_wrds_pgpass.py`
4. **LLM errors**: Validate keys with test scripts; try different model; check network/proxy
5. **Encoding/Emoji**: Use `-X utf8`; launcher handles chcp 65001
6. **Long analysis**: Normal for full 8-agent run (3-10min); use quicker models or reduced debate rounds in config
7. **A-shares/Crypto**: Verify smart router detection; some features still evolving

**Chinese Mainland Notes**:
- A-shares well-supported via akshare/efinance (no yfinance blocks)
- WRDS for US historical
- Use DeepSeek/Kimi for best Chinese language performance

---

## 🏗️ Architecture Highlights

- **LangGraph State**: `AgentState`, debate states, investment plan, final decision
- **Tool Nodes**: Abstracted in `agent_utils.py` (get_stock_data, get_indicators, get_fundamentals, get_news, etc.)
- **Conditional Edges**: Debate rounds limited, risk discussion, reflection triggers
- **Dataflows**: Pluggable vendors with fallback chains (`interface.py`)
- **Utils**: Core stock tools, technical indicators, trading signals, memory reflection

Extensible for more agents, data sources, or custom LLMs.

---

## 📚 Additional Documentation

- `PROJECT_MEMORY.md`: Detailed technical memory of v2.0 implementation
- `QUICK_START.md` / `new/QUICK_START_GUIDE.md`: Step-by-step
- `new/FINAL_INTEGRATION_SUMMARY.md`: Version comparisons (use **Integrated/Web**)
- `new/ACCE_v2.0.01_RELEASE.md`, `SYSTEM_COMPLETION_REPORT.md`: Completion reports
- `CRYPTO_TRADING_GUIDE.md`, `NEWS_ANALYSIS_GUIDE.md`, `WRDS_*_GUIDE.md`: Specialized guides
- `notebooks/`: Analytical Jupyter workflows
- `new/*.md`: Chinese detailed notes, performance reports, API configs

**For developers**: See `tradingagents/__init__.py`, `default_config.py`, agent implementations. Use `test_graph_direct.py` for graph testing.

---

## ⚠️ Disclaimer

This is a **research and educational tool**. All analysis, signals, and recommendations are for demonstration and learning purposes only. 

- Not investment advice
- Past performance ≠ future results
- LLM outputs can hallucinate - always verify with multiple sources
- API usage incurs costs (monitor DeepSeek/Gemini usage)
- WRDS requires valid academic credentials

**Use at your own risk.**

---

## 🚀 Next Steps & Roadmap

**Completed**:
- ✅ Full 8-agent LangGraph integration
- ✅ Web UI with real K-line + live WS
- ✅ Smart data routing (WRDS/akshare/efinance/CoinGecko)
- ✅ A-share + news (Claw) + crypto foundations
- ✅ Credential auto-loading + extensive tests
- ✅ Chinese/English bilingual reports
- ✅ Reflection memory system
- ✅ Performance optimizations & diagnostics

**Potential Enhancements** (from project memory):
- Crosshair/draggable chart interactions
- More indicators (RSI, MACD full integration in UI)
- PDF report export
- Multi-timeframe support
- Enhanced crypto real-time trading
- Portfolio optimization across assets
- Docker deployment
- Advanced visualization canvas

---

**Enjoy exploring the power of multi-agent AI for financial analysis!**

For issues, check test scripts first, then refer to `TROUBLESHOOTING.md` or run diagnostics.

*Consolidated from all project files, summaries, and code as of 2026-04-18.*
