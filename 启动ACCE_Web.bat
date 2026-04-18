@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ACCE v2.0 - Web 启动器

REM 始终使用本脚本所在目录作为项目根目录（可随意移动本文件）
set "ROOT=%~dp0"
cd /d "%ROOT%" || (
    echo [错误] 无法进入目录: %ROOT%
    pause
    exit /b 1
)

echo ================================================================================
echo                    ACCE v2.0 - Web 界面
echo ================================================================================
echo.
echo [目录] %ROOT%
echo [说明] 修改页面/CSS 后：先 Ctrl+C 停服，再重新运行本脚本；浏览器 Ctrl+F5 强刷
echo.

if not exist "%ROOT%is\wrds.txt" (
    echo [警告] 未找到 is\wrds.txt，WRDS 将无法自动连接。
    echo        请创建文件: %ROOT%is\wrds.txt
    echo        示例:
    echo          username: your_wrds_username
    echo          password: your_wrds_password
    echo.
)

if not exist "%ROOT%is\api assents.txt" (
    echo [警告] 未找到 is\api assents.txt，LLM 可能无法连接。
    echo        请创建文件: %ROOT%is\api assents.txt
    echo        示例:
    echo          deepseek: sk-xxxxxxxx
    echo          kimi: sk-xxxxxxxx
    echo          gemini: AIzaSyxxxxxxxx
    echo.
) else (
    echo [OK] 检测到 is\api assents.txt（LLM API 将自动加载，无需每次配置）
)

where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未在 PATH 中找到 python，请先安装 Python 3 并勾选「Add to PATH」。
    pause
    exit /b 1
)

echo [1/2] 安装/检查依赖...
if exist "%ROOT%web_requirements.txt" (
    python -m pip install -q -r "%ROOT%web_requirements.txt"
) else (
    python -m pip install -q flask flask-sock flask-cors python-dotenv
)

echo.
echo [2/2] 启动服务  http://localhost:5000
echo       按 Ctrl+C 停止
echo ================================================================================
echo.

python -X utf8 web_backend.py

echo.
echo 服务已停止
pause
endlocal
