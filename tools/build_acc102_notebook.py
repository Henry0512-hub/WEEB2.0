"""One-off script to emit notebooks/ACC102_Track4_Analytical_Workflow.ipynb."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "notebooks" / "ACC102_Track4_Analytical_Workflow.ipynb"

def md(s: str):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}

def code(s: str):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": s.splitlines(keepends=True),
    }

cells = [
    md("""# ACC102 — Track 4 Analytical Workflow

**Course:** ACC102 Mini Assignment (Python Data Product)  
**Track:** 4 — Interactive Data Analysis Tool (companion notebook)  
**Author:** *[Your name / ID]*  
**Date data accessed:** *[YYYY-MM-DD]*

This notebook documents a **coherent Python workflow** from problem definition to charts/tables, parallel to the Flask product (`web_backend.py`).
"""),
    md("""## 1. Analytical problem and target user

**Problem:** For a chosen **US equity ticker** and **calendar window**, summarise **daily OHLC** behaviour and simple **trend indicators** so a learner-investor can relate price action to the same window used in the interactive app.

**User:** A student or junior analyst using the web tool for **educational exploration** (not trading advice).

**Outcome:** Cleaned time series, descriptive statistics, and a price + moving-average chart reproducible in Python.
"""),
    md("""## 2. Data source and acknowledgement

- **Source:** Wharton Research Data Services (**WRDS**), CRSP daily stock file (`crsp.dsf`), joined with `crsp.msenames` for ticker mapping.
- **Retrieval:** Python `wrds` connector and SQL in project module `fast_chart_data.py` (`get_wrds_data`).
- **Access date:** Record the date you run this notebook in your reflection report.
- **Reliability:** Educational use; corporate actions and microstructure are not fully modelled here—see limitations below.
"""),
    code("""import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Project root (parent of /notebooks)
ROOT = Path.cwd().resolve()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fast_chart_data import get_wrds_data, calculate_indicators

%matplotlib inline
try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (10, 4)
plt.rcParams["axes.titlesize"] = 11
"""),
    code("""# Parameters — align with a test run of the web app
TICKER = "AAPL"
START_DATE = "2024-06-01"
END_DATE = "2024-08-15"

TICKER, START_DATE, END_DATE
"""),
    md("""## 3. Data acquisition

Loads daily OHLCV from WRDS. Requires valid WRDS credentials (`is/wrds.txt` or environment variables)—see `README_ACC102_Track4.md`.
"""),
    code("""df = get_wrds_data(TICKER, START_DATE, END_DATE)

if df is None or len(df) == 0:
    raise RuntimeError(
        "WRDS returned no rows. Check ticker, date range, and WRDS credentials. "
        "See README_ACC102_Track4.md."
    )

df.head()
"""),
    md("""## 4. Cleaning and preparation

The loader already applies basic cleaning (e.g. absolute prices, volume filter). Here we ensure **numeric types** and **monotonic dates** for analysis.
"""),
    code("""price_cols = ["OPEN", "HIGH", "LOW", "CLOSE"]
for c in price_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce").fillna(0).astype(int)

df = df.sort_index()
df = df[~df.index.duplicated(keep="last")]

print("Rows:", len(df))
print("Date range:", df.index.min().date(), "->", df.index.max().date())
df[price_cols + ["VOLUME"]].describe().round(4)
"""),
    md("""## 5. Analysis: indicators and visualisation

Rolling means come from `calculate_indicators`. We plot **close** and **MA20**.
"""),
    code("""indicators = calculate_indicators(df)
ma20 = pd.Series(indicators["MA20"], index=df.index)

fig, ax = plt.subplots()
ax.plot(df.index, df["CLOSE"], label="Close", color="#333333", linewidth=1.2)
ax.plot(df.index, ma20, label="MA20", color="#c0392b", linewidth=1.4)
ax.set_title(f"{TICKER} — Close and 20-day MA ({START_DATE} to {END_DATE})")
ax.set_ylabel("Price (USD)")
ax.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.show()

latest = df["CLOSE"].iloc[-1]
prev = df["CLOSE"].iloc[-2] if len(df) > 1 else latest
chg = latest - prev
chg_pct = 100 * chg / prev if prev != 0 else np.nan
print(f"Last close: {latest:.2f} | Daily change: {chg:+.2f} ({chg_pct:+.2f}%)")
"""),
    md("""## 6. Outputs linked to the interactive product

- **Tables / charts:** Above cells satisfy the notebook "tables, charts" requirement.
- **Web app:** Run `python web_backend.py` from the repo root; see `README_ACC102_Track4.md`.
"""),
    md("""## 7. Limitations (expand in your reflection)

- WRDS credentials may block external reproducibility—document access date and environment.
- Moving averages are descriptive, not predictive.
- LLM layers in the app are for commentary structure, not verified forecasts.
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

out.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")
print("Wrote", out)
