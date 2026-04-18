# TradingAgents 桌面快捷方式创建脚本

Write-Host "正在创建桌面快捷方式..." -ForegroundColor Green

# 获取当前脚本目录
$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 如果直接运行，使用 TradingAgents 目录
if (Test-Path "C:\Users\lenovo\TradingAgents") {
    $currentDir = "C:\Users\lenovo\TradingAgents"
}

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\TradingAgents.lnk")

$shortcut.TargetPath = "$currentDir\一键启动.bat"
$shortcut.WorkingDirectory = $currentDir
$shortcut.Description = "TradingAgents - AI股票分析系统"

$shortcut.Save()

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                  成功！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "桌面快捷方式已创建: TradingAgents.lnk" -ForegroundColor Yellow
Write-Host ""
Write-Host "双击桌面上的 'TradingAgents' 图标即可启动！" -ForegroundColor Green
Write-Host ""

# 询问是否立即打开 TradingAgents 文件夹
$answer = Read-Host "是否打开 TradingAgents 文件夹？(Y/N)"

if ($answer -eq "Y" -or $answer -eq "y") {
    Invoke-Item $currentDir
}
