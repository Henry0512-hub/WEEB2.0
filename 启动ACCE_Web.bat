@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ACCE v2.0 - Web

REM 项目根 = 本 bat 所在目录（请把本文件放在与 web_backend.py 同一层）
set "ROOT=%~dp0"
cd /d "%ROOT%" || (
    echo [错误] 无法进入目录: %ROOT%
    pause
    exit /b 1
)

if not exist "%ROOT%web_backend.py" (
    echo [错误] 当前目录下没有 web_backend.py
    echo.
    echo 当前路径: %ROOT%
    echo.
    echo 常见原因: 从 GitHub 下载 zip 后出现「双层文件夹」
    echo   请进入**内层**含有 web_backend.py 的文件夹，再双击本 bat，
    echo   或把本 bat 复制到与 web_backend.py 同一目录。
    echo.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo [错误] 未找到 python。请安装 Python 3.11+ 并勾选「Add Python to PATH」，
        echo       或在 Microsoft Store 安装 Python。
        pause
        exit /b 1
    )
    set "PY=py -3"
) else (
    set "PY=python"
)

echo ================================================================================
echo                    ACCE v2.0 - Web 界面
echo ================================================================================
echo [目录] %ROOT%
echo [Python] %PY%
echo.

if not exist "%ROOT%is\wrds.txt" (
    echo [提示] 未找到 is\wrds.txt 时 WRDS 不可用，可稍后配置。
    echo.
)

echo [1/2] 安装依赖 ^(若失败请看下方报错^) ...
if exist "%ROOT%web_requirements.txt" (
    %PY% -m pip install -r "%ROOT%web_requirements.txt"
) else (
    %PY% -m pip install flask flask-sock flask-cors python-dotenv
)
echo.

echo [2/2] 启动 http://localhost:5000  ^(Ctrl+C 停止^)
echo ================================================================================
echo.

%PY% -X utf8 "%ROOT%web_backend.py"
set "ERR=%ERRORLEVEL%"

echo.
if not "%ERR%"=="0" (
    echo [错误] 进程退出码: %ERR% 。请把上方黑色窗口里的英文报错复制下来排查。
) else (
    echo 服务已结束。
)
pause
endlocal
