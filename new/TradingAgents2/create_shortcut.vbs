Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 获取当前目录
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

' 创建快捷方式
Set shortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\TradingAgents.lnk")

shortcut.TargetPath = currentDir & "\一键启动.bat"
shortcut.WorkingDirectory = currentDir
shortcut.Description = "TradingAgents - AI股票分析系统"
shortcut.Save

MsgBox "桌面快捷方式已创建成功！" & vbCrLf & vbCrLf & "双击桌面上的 'TradingAgents' 图标即可启动", 64, "成功"
