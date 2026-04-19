# ACCE / WEEB2.0 — Quickstart (works after GitHub download)

## 1. Unzip

Use the folder that **directly contains** `web_backend.py` and `QUICKSTART.bat`.

If you see `WEEB2.0-main\WEEB2.0-main\`, open the **inner** folder until `web_backend.py` is visible.

## 2. Start the Web UI

**Double-click:** `QUICKSTART.bat` (recommended — all ASCII, no console garbling)

Or: `START_WEB.bat` / `启动ACCE_Web.bat` (they call the same script)

Browser: **http://localhost:5000**

## 3. Python

- Install **Python 3.11+** from [python.org](https://www.python.org/downloads/) and tick **Add python.exe to PATH**.
- If `python` is missing but the **Python Launcher** works, the batch file uses `py -3` automatically.

## 4. API keys (for real analysis)

Create folder **`is`** in the project root (next to `web_backend.py`).

**LLM — `is/api assents.txt`** (example):

```text
deepseek: sk-your-key
kimi: sk-your-key
gemini: AIza-your-key
```

**WRDS (optional) — `is/wrds.txt`:**

```text
username: your_wrds_username
password: your_wrds_password
```

Copy **`.env.example`** to **`.env`** if you use environment variables.

## 5. Command line (optional)

```bat
pip install -r web_requirements.txt
python -X utf8 web_backend.py
```

## 6. Trading 2.0 (optional crypto-off mode)

From project root:

```bat
python "Trading 2.0\start_web.py"
```

Or double-click **`Trading 2.0\START_WEB.bat`** (if present).

## Troubleshooting

| Problem | What to do |
|--------|------------|
| Black window shows garbage text | Use **`QUICKSTART.bat`** only; do not rely on old `.bat` files with Chinese inside. |
| `web_backend.py not found` | You are in the wrong folder; go one level deeper from the ZIP. |
| `Python not found` | Reinstall Python with **Add to PATH**, then open a new File Explorer window and double-click the bat again. |
| Port 5000 in use | Set `PORT=8080` in Environment Variables, or edit `web_backend.py` / use another free port. |

Full docs: `README.md`, `API_CONFIG_GUIDE.md`.
