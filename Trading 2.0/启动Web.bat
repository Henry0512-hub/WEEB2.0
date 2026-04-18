@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python -X utf8 "Trading 2.0\start_web.py"
pause
