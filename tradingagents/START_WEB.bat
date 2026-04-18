@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [ACCE] Starting Web http://localhost:5000  (Ctrl+C to stop)
echo.
python -X utf8 web_backend.py
if errorlevel 1 pause
