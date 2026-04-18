# Quick Start (5 Minutes)

This guide helps you run the current customized web version quickly.

## 1) Prerequisites

- Windows 10/11
- Python 3.11+ installed and in `PATH`
- Repository at `C:\Users\lenovo\TradingAgents`

## 2) Prepare Credentials

Create `is/wrds.txt`:

```text
username: your_wrds_username
password: your_wrds_password
```

Create `is/api assents.txt`:

```text
deepseek: sk-...
kimi: sk-...
gemini: AIza...
```

## 3) Start the App

From project root:

```bat
启动ACCE_Web.bat
```

When startup succeeds, open:

- [http://localhost:5000](http://localhost:5000)

## 4) Run One Analysis

In the page:

1. Select model (`DeepSeek`, `Kimi`, or `Gemini`)
2. Select market (`US`, `HK`, `CN`)
3. Input symbol (example: `AAPL`)
4. Select date range
5. Select report language (`中文` or `English`)
6. Click `开始分析`

You should see:
- chart data status
- progress polling
- final report output

## 5) Common Mistakes

- Wrong ticker (example: `APPL` is invalid, use `AAPL`)
- Missing `is/api assents.txt`
- Missing `is/wrds.txt`
- API key updated but backend not restarted

## 6) Quick Verification

Recommended smoke test:
- Model: DeepSeek
- Market: US
- Symbol: `AAPL`
- Date range: last 30-90 days
- Language: 中文

Expected:
- `/api/chart-data` returns success or clear fallback message
- `/api/analyze` returns task id
- `/api/task/<id>` reaches completed status
- report appears in middle panel

## 7) If Something Fails

- Restart launcher and retry
- Re-check credential file format and key values
- Ensure network can access provider endpoints
- Try another model to isolate provider-side issues

## 8) Useful Files

- `README.md` - full documentation
- `web_backend.py` - backend routes and task control
- `run_analysis_web.py` - analysis runner
- `templates/index.html` - frontend behavior
