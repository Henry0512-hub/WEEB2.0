@echo off
setlocal EnableExtensions
REM ASCII only - starts Trading 2.0 web (parent folder = project root)
set "PARENT=%~dp0.."
cd /d "%PARENT%" || (echo ERROR: cannot cd & pause & exit /b 1)

if not exist "%PARENT%\web_backend.py" (
    echo ERROR: web_backend.py not found. PARENT=%PARENT%
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (echo ERROR: Python not found & pause & exit /b 1)
    py -3 -m pip install -r "%PARENT%\web_requirements.txt"
    py -3 -X utf8 "%PARENT%\Trading 2.0\start_web.py"
) else (
    python -m pip install -r "%PARENT%\web_requirements.txt"
    python -X utf8 "%PARENT%\Trading 2.0\start_web.py"
)
pause
endlocal
