@echo off
chcp 65001 >nul
title NASA FIRMS 火点监测系统

echo ========================================
echo  NASA FIRMS 火点监测系统
echo ========================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装
    echo 请安装Python 3.7+
    pause
    exit /b 1
)

echo [信息] 启动系统...
python start_system.py

pause