@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m pip install -U pip
pip install -r web_requirements.txt
if exist requirements.txt pip install -r requirements.txt
echo.
pause
