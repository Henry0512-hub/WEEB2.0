@echo off
chcp 65001 >nul
title ACCE v2.0 - 集成版完整分析系统

REM Set Python path
set PYTHON_PATH=C:\Users\lenovo\AppData\Local\Programs\Python\Python313\python.exe

REM Set working directory to TradingAgents
set WORK_DIR=C:\Users\lenovo\TradingAgents

REM API Keys location
set WRDS_CREDS=%WORK_DIR%\id.txt
set AV_API=%WORK_DIR%\av api.txt
set LLM_API=%USERPROFILE%\Desktop\new\api assents.txt

echo ================================================================================
echo                    ACCE v2.0 - 集成版完整分析系统
echo ================================================================================
echo.
echo Version: 2.0.01 (Integrated)
echo Working Directory: %WORK_DIR%
echo.
echo API Keys:
echo   - WRDS: %WRDS_CREDS%
echo   - Alpha Vantage: %AV_API%
echo   - LLM APIs: %LLM_API%
echo.
echo Features:
echo   [*] 完整TradingAgents框架（8个AI智能体协同工作）
echo   [*] API密钥自动加载（从文件）
echo   [*] WRDS优先级设置（2024-12-31之前自动使用）
echo   [*] 交互式用户界面
echo   [*] 技术+基本面+情绪完整分析
echo   [*] 智能投资建议
echo.
echo ================================================================================
echo.
echo Starting integrated system...
echo.

REM Change to TradingAgents directory
cd /d "%WORK_DIR%"

REM Run integrated analysis system
"%PYTHON_PATH%" run_integrated_analysis.py

echo.
echo ================================================================================
echo System Exit
echo ================================================================================
echo.
pause
