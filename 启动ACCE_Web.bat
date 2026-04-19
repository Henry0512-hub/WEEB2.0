@echo off
REM ASCII only - forwards to QUICKSTART.bat (avoids UTF-8/GBK mojibake in CMD)
cd /d "%~dp0"
call "%~dp0QUICKSTART.bat"
