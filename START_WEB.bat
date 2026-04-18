@echo off
REM English filename - use this if the Chinese-named launcher fails to run
setlocal EnableExtensions
chcp 65001 >nul
title ACCE Web

set "ROOT=%~dp0"
cd /d "%ROOT%" || (echo ERROR: cannot cd to %ROOT% & pause & exit /b 1)

if not exist "%ROOT%web_backend.py" (
    echo ERROR: web_backend.py not found here:
    echo   %ROOT%
    echo.
    echo Open the INNER folder that contains web_backend.py (GitHub zips often have nested folders).
    echo.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python not in PATH. Install Python 3.11+ with "Add to PATH".
        pause
        exit /b 1
    )
    set "PY=py -3"
) else (
    set "PY=python"
)

echo ROOT: %ROOT%
echo Python: %PY%
echo.

if exist "%ROOT%web_requirements.txt" (
    echo Installing web_requirements.txt ...
    %PY% -m pip install -r "%ROOT%web_requirements.txt"
) else (
    %PY% -m pip install flask flask-sock flask-cors python-dotenv
)
echo.

echo Starting http://localhost:5000
%PY% -X utf8 "%ROOT%web_backend.py"
echo Exit code: %ERRORLEVEL%
pause
endlocal
