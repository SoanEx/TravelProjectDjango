@echo off
REM 確定當前目錄是批次檔所在目錄
cd /d %~dp0

REM 確保使用管理員權限執行腳本
echo Checking for administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo You need to run this script as Administrator.
    echo Exiting...
    pause
    exit /b
)

REM 執行 PowerShell 腳本
echo Starting project setup...
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

REM 完成提示
echo Project setup completed.
pause
