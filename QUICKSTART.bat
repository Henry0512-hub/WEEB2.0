@echo off
setlocal EnableExtensions
REM All ASCII - safe on any Windows code page (no mojibake after GitHub download)
title ACCE Web Quickstart

set "ROOT=%~dp0"
cd /d "%ROOT%" || (
    echo [ERROR] Cannot cd to: %ROOT%
    pause
    exit /b 1
)

if not exist "%ROOT%web_backend.py" (
    echo [ERROR] web_backend.py not found in:
    echo   %ROOT%
    echo.
    echo GitHub ZIPs are often nested. Open the INNER folder until you see web_backend.py,
    echo then double-click QUICKSTART.bat again.
    echo.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 goto :trypy
set "HASPY=1"
goto :deps

:trypy
where py >nul 2>&1
if errorlevel 1 goto :nopy
set "HASPY=0"
goto :deps

:nopy
echo [ERROR] Python not in PATH.
echo Install Python 3.11+ from https://www.python.org/downloads/
echo On the installer, enable "Add python.exe to PATH", then re-open this window.
pause
exit /b 1

:deps
echo ============================================================
echo  ACCE Web Quickstart
echo ============================================================
echo Root: %ROOT%
if "%HASPY%"=="1" (echo Using: python) else (echo Using: py -3)
echo.

echo [1/2] Installing dependencies...
if exist "%ROOT%web_requirements.txt" (
    if "%HASPY%"=="1" (
        python -m pip install -r "%ROOT%web_requirements.txt"
    ) else (
        py -3 -m pip install -r "%ROOT%web_requirements.txt"
    )
) else (
    if "%HASPY%"=="1" (
        python -m pip install flask flask-sock flask-cors python-dotenv
    ) else (
        py -3 -m pip install flask flask-sock flask-cors python-dotenv
    )
)
echo.

echo [2/2] Starting server...
echo Open in browser: http://localhost:5000
echo Press Ctrl+C in this window to stop.
echo ============================================================
echo.

if "%HASPY%"=="1" (
    python -X utf8 "%ROOT%web_backend.py"
) else (
    py -3 -X utf8 "%ROOT%web_backend.py"
)

echo.
echo Server stopped. Code: %ERRORLEVEL%
echo See QUICKSTART.md for API keys and troubleshooting.
pause
endlocal
