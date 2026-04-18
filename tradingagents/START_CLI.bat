@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [ACCE] Interactive CLI (run_integrated_analysis.py)
echo.
python -X utf8 run_integrated_analysis.py
pause
