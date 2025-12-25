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

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [信息] 虚拟环境已激活
) else (
    echo [信息] 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM 安装依赖
echo [信息] 安装依赖...
pip install flask requests pandas pymysql python-dotenv -q

REM 检查MySQL服务
echo [信息] 检查MySQL服务...
sc query mysql | findstr "RUNNING" >nul
if errorlevel 1 (
    echo [警告] MySQL服务未运行
    echo 尝试启动MySQL服务...
    net start mysql >nul 2>&1
    if errorlevel 1 (
        echo [错误] 无法启动MySQL服务
        echo 请手动启动: net start mysql
        pause
        exit /b 1
    )
    echo [成功] MySQL服务已启动
)

REM 创建数据库
echo [信息] 设置数据库...
python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='password')
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS fire_monitor')
    print('数据库已准备就绪')
except Exception as e:
    print(f'数据库设置失败: {e}')
    exit(1)
"

REM 创建.env文件
if not exist ".env" (
    echo [信息] 创建.env文件...
    echo NASA_API_KEY=DEMO_KEY > .env
    echo DATABASE_URL=mysql+pymysql://root:password@localhost/fire_monitor >> .env
    echo FLASK_ENV=development >> .env
    echo SECRET_KEY=dev-key-123 >> .env
)

REM 运行简单启动脚本
echo [信息] 启动系统...
echo 请稍候...
start "" "cmd /k python scripts/start_simple.py"

echo.
echo ========================================
echo [成功] 系统正在启动!
echo ========================================
echo Web界面: http://localhost:5000
echo 按任意键打开浏览器...
pause >nul
start http://localhost:5000

echo.
echo 要停止系统，请关闭所有打开的CMD窗口
echo ========================================
pause