@echo off
chcp 65001 >nul
title TradingAgents 增强分析系统

REM 设置Python路径
set PYTHON_PATH=C:\Users\lenovo\AppData\Local\Programs\Python\Python313\python.exe

echo ======================================================================
echo           TradingAgents 增强分析系统 v2.0
echo ======================================================================
echo.
echo 支持的分析师:
echo   1. DeepSeek 分析师    (推荐) - 最便宜: Y1/百万tokens
echo   2. Kimi 分析师        (中文) - 128k上下文, 中文最强
echo   3. Gemini 分析师      (免费) - 每天1500次免费
echo.
echo ======================================================================
echo.

REM 第一步：选择分析师
set /p llm_choice=请选择您的分析师 (输入 1-3):

if "%llm_choice%"=="1" (
    set analyst_name=DeepSeek
    echo [确认] 您选择了 DeepSeek 分析师
) else if "%llm_choice%"=="2" (
    set analyst_name=Kimi
    echo [确认] 您选择了 Kimi 分析师
) else if "%llm_choice%"=="3" (
    set analyst_name=Gemini
    echo [确认] 您选择了 Gemini 分析师
) else (
    echo [错误] 无效的选择
    pause
    exit
)

echo.
echo ======================================================================
echo.

REM 第二步：输入股票代码
echo 常见股票代码:
echo - 美股: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN
echo - 中概股: BABA, JD, PDD, BIDU
echo - 加密货币: BTC-USD, ETH-USD
echo.
set /p ticker=请输入股票代码:

echo.
echo ======================================================================
echo.

REM 第三步：输入日期范围
echo 系统将根据开始日期自动选择数据源:
echo.
echo - 开始日期 2024-12-31 及以前: 使用 WRDS 学术数据库 + 新闻
echo - 开始日期 2024-12-31 以后:     使用实时新闻 + 基本面数据
echo.
echo 示例日期范围:
echo - 开始: 2024-06-15, 结束: 2024-08-15 (使用WRDS, 2个月分析)
echo - 开始: 2025-01-15, 结束: 2025-03-20 (使用实时数据, 2个月分析)
echo - 开始: 2025-03-01, 结束: 2025-04-09 (使用实时数据, 1个月分析)
echo.
set /p start_date=请输入开始日期 (格式: YYYY-MM-DD):

REM 如果结束日期为空，使用今天
set /p end_date=请输入结束日期 (格式: YYYY-MM-DD, 默认今天):

if "%end_date%"=="" (
    REM 获取今天的日期
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
    set end_date=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
    echo [默认] 使用今天作为结束日期: %end_date%
)

echo.
echo [确认] 分析日期范围: %start_date% 到 %end_date%

REM 计算天数差
for /f "delims=" %%D in ('powershell -command "$start = Get-Date -Date '%start_date%'; $end = Get-Date -Date '%end_date%'; ($end - $start).Days"') do set days=%%D
echo [计算] 分析周期: %days% 天

echo.
echo ======================================================================
echo.

REM 第四步：选择分析类型
echo 可用的分析类型:
echo   1. 完整分析 (推荐)
echo      - 技术面分析
echo      - 基本面分析
echo      - 情绪面分析 (新闻情感)
echo      - 综合投资建议
echo.
echo   2. 快速分析
echo      - 技术面分析
echo      - 基本面分析
echo.
echo   3. 情绪分析
echo      - 新闻情感分析
echo      - 市场情绪评估
echo.
set /p analysis_type=请选择分析类型 (输入 1-3, 默认1):

if "%analysis_type%"=="" set analysis_type=1

if "%analysis_type%"=="1" (
    set analysis_name=完整分析
) else if "%analysis_type%"=="2" (
    set analysis_name=快速分析
) else if "%analysis_type%"=="3" (
    set analysis_name=情绪分析
) else (
    set analysis_name=完整分析
    set analysis_type=1
)

echo [确认] 分析类型: %analysis_name%

echo.
echo ======================================================================
echo.
echo 正在启动分析系统...
echo.

REM 切换到TradingAgents目录
cd /d C:\Users\lenovo\TradingAgents

REM 调用分析脚本
"%PYTHON_PATH%" run_enhanced_analysis.py %ticker% %start_date% %end_date% %llm_choice% %analysis_type%

echo.
echo ======================================================================
echo 分析完成！
echo ======================================================================
echo.
pause
