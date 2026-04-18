@echo off
chcp 65001 >nul
echo ============================================================
echo           TradingAgents 一键启动脚本
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python 已安装
echo.

REM 检查是否在正确的目录
if not exist "run_with_deepseek.py" (
    echo [错误] 请在 TradingAgents 目录下运行此脚本
    pause
    exit /b 1
)

echo ============================================================
echo           选择启动模式
echo ============================================================
echo.
echo 1. DeepSeek 模式 (推荐) - 性价比最高
echo 2. Kimi 模式 - 中文最好
echo 3. Gemini 模式 - 免费(需翻墙)
echo 4. 测试 API 连接
echo 5. 查看配置状态
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto deepseek
if "%choice%"=="2" goto kimi
if "%choice%"=="3" goto gemini
if "%choice%"=="4" goto test
if "%choice%"=="5" goto status

echo [错误] 无效选项
pause
exit /b 1

:deepseek
echo.
echo ============================================================
echo           启动 DeepSeek 模式
echo ============================================================
echo.
python run_with_deepseek.py
pause
exit /b 0

:kimi
echo.
echo ============================================================
echo           启动 Kimi 模式
echo ============================================================
echo.
python run_with_kimi.py
pause
exit /b 0

:gemini
echo.
echo ============================================================
echo           启动 Gemini 模式
echo ============================================================
echo.
echo [提示] Gemini 需要能访问 Google
echo.
python run_with_gemini.py
pause
exit /b 0

:test
echo.
echo ============================================================
echo           测试 API 连接
echo ============================================================
echo.
echo 测试 DeepSeek...
python test_deepseek_simple.py
echo.
echo.
echo 测试 Kimi...
python test_kimi.py
echo.
echo.
echo 测试 Gemini...
python test_gemini_simple.py
echo.
pause
exit /b 0

:status
echo.
echo ============================================================
echo           配置状态
echo ============================================================
echo.

REM 检查 .env 文件
if exist ".env" (
    echo [OK] .env 文件存在

    REM 检查 API Keys
    findstr /C:"OPENAI_API_KEY" .env >nul
    if not errorlevel 1 echo [OK] DeepSeek API Key 已配置

    findstr /C:"GOOGLE_API_KEY" .env >nul
    if not errorlevel 1 echo [OK] Gemini API Key 已配置

    findstr /C:"KIMI_API_KEY" .env >nul
    if not errorlevel 1 echo [OK] Kimi API Key 已配置
) else (
    echo [警告] .env 文件不存在
)

echo.
echo 已安装的组件:
echo.

REM 检查 crawl4ai
python -c "import crawl4ai" >nul 2>&1
if not errorlevel 1 echo [OK] crawl4ai (Claw 新闻爬虫)

REM 检查 akshare
python -c "import akshare" >nul 2>&1
if not errorlevel 1 echo [OK] akshare (中国股市数据)

REM 检查 fredapi
python -c "import fredapi" >nul 2>&1
if not errorlevel 1 echo [OK] fredapi (宏观经济数据)

REM 检查 yfinance
python -c "import yfinance" >nul 2>&1
if not errorlevel 1 echo [OK] yfinance (美股数据)

echo.
echo ============================================================
echo.
pause
exit /b 0
