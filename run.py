#!/usr/bin/env python3
"""
NASA FIRMS 火点监测系统 - 一键启动脚本 (Windows兼容版)
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_windows_encoding():
    """设置Windows编码"""
    if sys.platform == 'win32':
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass
        
        # 设置标准输出编码
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_and_setup_mysql():
    """检查和设置MySQL"""
    print("\n检查并设置MySQL数据库...")
    
    try:
        # 运行MySQL配置工具
        result = subprocess.run(
            [sys.executable, "scripts/check_mysql.py"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✓ MySQL设置成功")
            return True
        else:
            print(f"✗ MySQL设置失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ MySQL检查失败: {e}")
        return False

def check_python_dependencies():
    """检查Python依赖"""
    print("\n检查Python依赖...")
    
    required = [
        'flask',
        'requests',
        'pandas',
        'pymysql',
        'python-dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print("正在安装...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing + ["-q"])
            print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("✗ 依赖安装失败")
            return False
    else:
        print("✓ 所有依赖已安装")
        return True

def setup_project_directories():
    """创建项目目录"""
    print("\n设置项目目录...")
    
    directories = [
        'logs',
        'data',
        'templates',
        'static/css',
        'static/js',
        'static/images'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ 目录结构已创建")

def create_env_file():
    """创建环境配置文件"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("\n创建环境配置文件...")
        
        env_content = """# NASA FIRMS 火点监测系统
# 配置说明

# NASA API密钥（获取地址: https://firms.modaps.eosdis.nasa.gov/api/map_key/）
NASA_API_KEY=DEMO_KEY

# 数据库配置（自动检测）
# DATABASE_URL=mysql+pymysql://root:password@localhost/fire_monitor
# 或使用SQLite: DATABASE_URL=sqlite:///fire_monitor.db

# Flask配置
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✓ .env文件已创建")
        print("  请编辑此文件设置您的NASA API密钥")
    
    return True

def start_web_application():
    """启动Web应用"""
    print("\n启动Web应用...")
    
    # 创建简单的Web应用
    web_app_code = '''
from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 基础目录
BASE_DIR = Path(__file__).parent.parent

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API状态"""
    return jsonify({
        'status': 'running',
        'service': 'NASA FIRMS Fire Monitor',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/map')
def map_view():
    """地图页面"""
    return render_template('map.html')

if __name__ == '__main__':
    # 确保模板目录存在
    templates_dir = BASE_DIR / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # 创建基础模板
    if not (templates_dir / 'index.html').exists():
        create_basic_templates()
    
    print("=" * 60)
    print("NASA FIRMS 火点监测系统")
    print("访问地址: http://localhost:5000")
    print("API状态: http://localhost:5000/api/status")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_basic_templates():
    """创建基础模板"""
    templates_dir = BASE_DIR / 'templates'
    
    # index.html
    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASA FIRMS 火点监测系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .hero { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 2rem;
            border-radius: 0 0 20px 20px;
            margin-bottom: 3rem;
        }
        .card { 
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1 class="display-4">🔥 NASA FIRMS 火点监测系统</h1>
            <p class="lead">基于NASA卫星数据的实时火点监测平台</p>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📡 实时数据</h5>
                        <p class="card-text">从NASA FIRMS API获取最新的卫星火点数据</p>
                        <div id="data-status">加载中...</div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🗺️ 交互地图</h5>
                        <p class="card-text">在地图上可视化显示火点位置和详细信息</p>
                        <a href="/map" class="btn btn-primary">查看地图</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📊 数据分析</h5>
                        <p class="card-text">分析火点趋势、分布和统计数据</p>
                        <button class="btn btn-outline-primary" onclick="loadStats()">查看统计</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">系统状态</h5>
                <div id="system-status"></div>
            </div>
        </div>
    </div>
    
    <script>
        // 加载系统状态
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('system-status').innerHTML = `
                    <div class="alert alert-success">
                        <strong>系统状态:</strong> 运行正常<br>
                        <strong>服务:</strong> ${data.service}<br>
                        <strong>时间:</strong> ${new Date(data.timestamp).toLocaleString()}
                    </div>
                `;
            } catch (error) {
                document.getElementById('system-status').innerHTML = `
                    <div class="alert alert-warning">
                        <strong>系统状态:</strong> 连接异常<br>
                        <small>${error}</small>
                    </div>
                `;
            }
        }
        
        // 每10秒更新状态
        loadStatus();
        setInterval(loadStatus, 10000);
        
        function loadStats() {
            alert('统计功能正在开发中...');
        }
    </script>
</body>
</html>"""
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # map.html
    map_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>火点地图 - NASA FIRMS</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        #map { height: 85vh; }
        body { margin: 0; }
        .navbar { background: #667eea; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                🔥 NASA FIRMS 火点地图
            </a>
            <div>
                <a href="/" class="btn btn-light btn-sm">返回首页</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid px-0">
        <div id="map"></div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // 初始化地图
        const map = L.map('map').setView([30, 110], 4);
        
        // 添加地图图层
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        // 添加示例火点
        const exampleFires = [
            {lat: 36.62, lng: 117.32, conf: 'high', name: '示例火点1'},
            {lat: 34.05, lng: 118.24, conf: 'medium', name: '示例火点2'},
            {lat: 31.23, lng: 121.47, conf: 'low', name: '示例火点3'}
        ];
        
        exampleFires.forEach(fire => {
            let color = '#FF5722';
            if (fire.conf === 'high') color = '#F44336';
            if (fire.conf === 'medium') color = '#FF9800';
            if (fire.conf === 'low') color = '#FFC107';
            
            L.circleMarker([fire.lat, fire.lng], {
                radius: 10,
                color: color,
                fillColor: color,
                fillOpacity: 0.7
            }).addTo(map)
            .bindPopup(`<b>${fire.name}</b><br>置信度: ${fire.conf}`);
        });
        
        // 添加比例尺
        L.control.scale().addTo(map);
        
        // 提示信息
        const info = L.control({position: 'bottomright'});
        info.onAdd = function() {
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        };
        info.update = function(props) {
            this._div.innerHTML = '<h6>🔥 火点地图</h6>' +
                '红色: 高置信度<br>' +
                '橙色: 中置信度<br>' +
                '黄色: 低置信度<br>' +
                '<small>真实数据需要运行爬虫</small>';
        };
        info.addTo(map);
    </script>
</body>
</html>"""
    
    with open(templates_dir / 'map.html', 'w', encoding='utf-8') as f:
        f.write(map_html)
    
    print("✓ 基础模板已创建")
'''
    
    # 保存Web应用代码
    web_app_file = 'simple_web_app.py'
    with open(web_app_file, 'w', encoding='utf-8') as f:
        f.write(web_app_code)
    
    # 启动Web应用
    print("正在启动Web服务器...")
    
    try:
        # 在后台启动Web应用
        import threading
        
        def run_web():
            os.system(f'"{sys.executable}" {web_app_file}')
        
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()
        
        print("✓ Web应用已启动")
        print("  访问: http://localhost:5000")
        
        return True
    except Exception as e:
        print(f"✗ 启动Web应用失败: {e}")
        return False

def start_crawler_service():
    """启动爬虫服务"""
    print("\n启动数据爬虫...")
    
    # 创建简单爬虫
    crawler_code = '''
#!/usr/bin/env python3
"""
简单NASA数据爬虫
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime
import os

def fetch_nasa_fire_data():
    """获取NASA火点数据"""
    print(f"{datetime.now()}: 开始获取NASA数据...")
    
    try:
        # 使用NASA的DEMO_KEY
        url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/DEMO_KEY/VIIRS_SNPP_NRT/1"
        
        print(f"请求URL: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if response.text.strip():
            df = pd.read_csv(pd.io.common.StringIO(response.text))
            
            print(f"获取到 {len(df)} 条火点记录")
            
            # 保存数据
            save_data(df)
            
            return True
        else:
            print("API返回空数据")
            return False
            
    except Exception as e:
        print(f"获取数据失败: {e}")
        return False

def save_data(df):
    """保存数据"""
    # 创建数据目录
    os.makedirs('data', exist_ok=True)
    
    # 保存为CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'data/fire_data_{timestamp}.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    print(f"数据已保存: {csv_file}")
    
    # 保存为JSON（用于Web显示）
    json_file = 'data/latest_fires.json'
    
    # 转换为适合Web显示的格式
    fires = []
    for _, row in df.head(100).iterrows():  # 只取前100条
        try:
            fire = {
                'latitude': float(row.get('latitude', 0)),
                'longitude': float(row.get('longitude', 0)),
                'confidence': str(row.get('confidence', '')),
                'satellite': str(row.get('satellite', '')),
                'frp': float(row.get('frp', 0)),
                'acq_date': str(row.get('acq_date', '')),
                'acq_time': str(row.get('acq_time', ''))
            }
            fires.append(fire)
        except:
            continue
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'count': len(fires),
            'timestamp': datetime.now().isoformat(),
            'data': fires
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON数据已保存: {json_file}")

def run_continuous(interval_minutes=10):
    """连续运行爬虫"""
    print("="*60)
    print("NASA FIRMS 数据爬虫启动")
    print(f"每 {interval_minutes} 分钟运行一次")
    print("="*60)
    
    try:
        while True:
            fetch_nasa_fire_data()
            print(f"等待 {interval_minutes} 分钟...")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print("爬虫停止")

if __name__ == '__main__':
    # 先运行一次
    fetch_nasa_fire_data()
    
    # 然后按间隔运行
    run_continuous(interval_minutes=10)
'''
    
    # 保存爬虫代码
    crawler_file = 'simple_crawler.py'
    with open(crawler_file, 'w', encoding='utf-8') as f:
        f.write(crawler_code)
    
    # 启动爬虫
    try:
        import threading
        
        def run_crawler():
            os.system(f'"{sys.executable}" {crawler_file}')
        
        crawler_thread = threading.Thread(target=run_crawler, daemon=True)
        crawler_thread.start()
        
        print("✓ 数据爬虫已启动")
        print("  每10分钟获取一次NASA数据")
        
        return True
    except Exception as e:
        print(f"✗ 启动爬虫失败: {e}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("NASA FIRMS 火点监测系统 - 一键启动")
    print("="*60)
    
    # 设置Windows编码
    setup_windows_encoding()
    
    # 检查Python依赖
    if not check_python_dependencies():
        print("✗ 依赖检查失败，程序退出")
        sys.exit(1)
    
    # 创建项目目录
    setup_project_directories()
    
    # 创建环境文件
    create_env_file()
    
    # 检查和设置MySQL
    if not check_and_setup_mysql():
        print("✗ MySQL设置失败")
        print("\n尝试使用简化模式继续...")
    
    # 启动Web应用
    if not start_web_application():
        print("✗ Web应用启动失败")
    
    # 启动爬虫
    if not start_crawler_service():
        print("✗ 爬虫启动失败")
    
    print("\n" + "="*60)
    print("✅ 系统启动完成!")
    print("="*60)
    print("\n重要信息:")
    print("1. Web界面: http://localhost:5000")
    print("2. 地图页面: http://localhost:5000/map")
    print("3. 数据目录: ./data/")
    print("4. 日志文件: ./logs/")
    print("="*60)
    
    print("\n⚠️  注意事项:")
    print("• DEMO_KEY有使用限制，建议注册获取自己的API密钥")
    print("• 获取地址: https://firms.modaps.eosdis.nasa.gov/api/map_key/")
    print("• 将API密钥添加到 .env 文件的 NASA_API_KEY")
    print("="*60)
    
    print("\n按 Ctrl+C 停止系统...")
    
    try:
        # 保持主线程运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止系统...")
        sys.exit(0)

if __name__ == '__main__':
    main()