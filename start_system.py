#!/usr/bin/env python3
"""
启动NASA FIRMS系统
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def setup_environment():
    """设置环境"""
    print("=" * 60)
    print("NASA FIRMS 火点监测系统")
    print("=" * 60)
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    # 检查依赖
    print("\n检查依赖...")
    required = ['flask', 'requests', 'pandas', 'python-dotenv']
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"安装依赖: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    
    print("✅ 环境准备完成")

def start_web_app():
    """启动Web应用"""
    print("\n启动Web应用...")
    
    try:
        # 在后台启动Web应用
        def run_web():
            os.system(f'"{sys.executable}" simple_web_app.py')
        
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()
        
        time.sleep(3)  # 等待Web应用启动
        
        print("✅ Web应用已启动")
        print("   访问: http://localhost:5000")
        
        return True
    except Exception as e:
        print(f"❌ 启动Web应用失败: {e}")
        return False

def start_crawler():
    """启动数据爬虫"""
    print("\n启动数据爬虫...")
    
    try:
        # 在后台启动爬虫
        def run_crawler():
            os.system(f'"{sys.executable}" simple_crawler.py')
        
        crawler_thread = threading.Thread(target=run_crawler, daemon=True)
        crawler_thread.start()
        
        print("✅ 数据爬虫已启动")
        print("   每10分钟自动获取NASA数据")
        
        return True
    except Exception as e:
        print(f"❌ 启动爬虫失败: {e}")
        return False

def main():
    """主函数"""
    # 设置环境
    setup_environment()
    
    print("\n" + "=" * 60)
    print("选择运行模式:")
    print("1. 启动完整系统（Web + 爬虫）")
    print("2. 仅启动Web应用")
    print("3. 仅启动数据爬虫")
    print("4. 退出")
    print("=" * 60)
    
    try:
        choice = input("\n请选择 (1-4): ").strip()
    except:
        choice = '1'
    
    if choice == '1':
        print("\n启动完整系统...")
        start_web_app()
        time.sleep(2)
        start_crawler()
        
        print("\n" + "=" * 60)
        print("✅ 系统已启动！")
        print("=" * 60)
        print("\n重要链接:")
        print("• 主界面: http://localhost:5000")
        print("• 地图: http://localhost:5000/map")
        print("• 数据API: http://localhost:5000/api/fires")
        print("\n数据目录: ./data/")
        print("\n按 Ctrl+C 停止系统")
        print("=" * 60)
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止系统...")
    
    elif choice == '2':
        start_web_app()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nWeb应用已停止")
    
    elif choice == '3':
        start_crawler()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n爬虫已停止")
    
    else:
        print("退出")

if __name__ == '__main__':
    main()