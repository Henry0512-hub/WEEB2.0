@echo off
echo 正在创建桌面快捷方式...

PowerShell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\TradingAgents.lnk'); $s.TargetPath = '%~dp0一键启动.bat'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'TradingAgents - AI股票分析系统'; $s.Save()"

if exist "%USERPROFILE%\Desktop\TradingAgents.lnk" (
    echo.
    echo ============================================================
    echo                  成功！
    echo ============================================================
    echo.
    echo 桌面快捷方式已创建: TradingAgents.lnk
    echo.
    echo 双击桌面上的 "TradingAgents" 图标即可启动！
    echo.
    pause
) else (
    echo.
    echo 创建失败，请手动创建快捷方式
    echo.
    pause
)
