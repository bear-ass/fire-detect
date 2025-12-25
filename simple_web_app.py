#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NASA FIRMS 火点监测系统 - 红色圆点版
✅ 地图居中缩小 40%
✅ 火点以红色圆点显示（带脉冲动画）
✅ 底部美化数据面板
"""

import os
import pymysql
from flask import Flask, render_template_string

# ================== 配置区 ==================
APP_NAME = "🔥 NASA 火点实时监测（测试版）"

TIANDITU_KEY = "75e04b57738931d9f62f916d74bddf4b"  # ⚠️ 替换为你的 Key

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # ⚠️ 改这里！
    'database': 'fire_monitoring',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

os.environ["FLASK_SKIP_DOTENV"] = "1"
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def get_fire_points_from_db(limit: int = 500):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT lat, lng, time
                FROM fire_points
                WHERE lat IS NOT NULL AND lng IS NOT NULL
                ORDER BY time DESC
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
        connection.close()
        return results
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return []


@app.route('/')
def index():
    fires = get_fire_points_from_db(limit=200)

    fire_list = []
    for row in fires:
        fire_list.append({
            'lat': float(row['lat']),
            'lng': float(row['lng']),
            'acq_date': str(row['time']),
        })

    HTML = (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>{{ app_name }}</title>\n'
        '    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">\n'
        '    <style>\n'
        '        body {\n'
        '            background: #f8f9fa;\n'
        '            margin: 0;\n'
        '            padding: 0;\n'
        '            font-family: "Segoe UI", Arial, sans-serif;\n'
        '            display: flex;\n'
        '            flex-direction: column;\n'
        '            height: 100vh;\n'
        '        }\n'
        '        .header {\n'
        '            background: linear-gradient(135deg, #c62828, #d32f2f);\n'
        '            color: white;\n'
        '            padding: 1rem;\n'
        '            text-align: center;\n'
        '            box-shadow: 0 2px 6px rgba(0,0,0,0.1);\n'
        '        }\n'
        '        .map-container {\n'
        '            flex: 1;\n'
        '            display: flex;\n'
        '            justify-content: center;\n'
        '            align-items: center;\n'
        '            overflow: hidden;\n'
        '            background: #e9ecef;\n'
        '        }\n'
        '        .map-wrapper {\n'
        '            width: 100%;\n'
        '            height: 100%;\n'
        '            max-width: 1200px;\n'
        '            max-height: 600px;\n'
        '            display: flex;\n'
        '            justify-content: center;\n'
        '            align-items: center;\n'
        '        }\n'
        '        #map {\n'
        '            width: 100%;\n'
        '            height: 100%;\n'
        '            transform: scale(0.6);\n'
        '            transform-origin: center center;\n'
        '        }\n'
        '        .data-panel {\n'
        '            width: 100%;\n'
        '            max-height: 35vh;\n'
        '            background: white;\n'
        '            border-top: 1px solid #dee2e6;\n'
        '            padding: 1.2rem;\n'
        '            overflow-y: auto;\n'
        '            box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);\n'
        '        }\n'
        '        .data-panel h5 {\n'
        '            margin-top: 0;\n'
        '            color: #495057;\n'
        '            font-weight: 600;\n'
        '        }\n'
        '        table th, table td {\n'
        '            text-align: center;\n'
        '            vertical-align: middle;\n'
        '            font-size: 0.92rem;\n'
        '        }\n'
        '        table th {\n'
        '            background-color: #f1f3f5;\n'
        '        }\n'
        '        /* 脉冲动画 */\n'
        '        .pulse-circle {\n'
        '            animation: pulseCircle 2s infinite;\n'
        '        }\n'
        '        @keyframes pulseCircle {\n'
        '            0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }\n'
        '            70% { box-shadow: 0 0 0 8px rgba(220, 53, 69, 0); }\n'
        '            100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }\n'
        '        }\n'
        '    </style>\n'
        '    <script src="https://api.tianditu.gov.cn/api?v=4.0&tk={{ tianditu_key }}"></script>\n'
        '</head>\n'
        '<body>\n'
        '    <div class="header">\n'
        '        <h2>{{ app_name }}</h2>\n'
        '        <p>共加载 {{ fire_count }} 个火点</p>\n'
        '    </div>\n'
        '\n'
        '    <div class="map-container">\n'
        '        <div class="map-wrapper">\n'
        '            <div id="map"></div>\n'
        '        </div>\n'
        '    </div>\n'
        '\n'
        '    <div class="data-panel">\n'
        '        <h5>📊 已加载火点数据（{{ fire_count }} 条）</h5>\n'
        '        <table class="table table-hover table-sm">\n'
        '            <thead>\n'
        '                <tr>\n'
        '                    <th>#</th>\n'
        '                    <th>经度 (Lng)</th>\n'
        '                    <th>纬度 (Lat)</th>\n'
        '                    <th>时间</th>\n'
        '                </tr>\n'
        '            </thead>\n'
        '            <tbody>\n'
        '                {% for fire in fire_data %}\n'
        '                <tr>\n'
        '                    <td>{{ loop.index }}</td>\n'
        '                    <td>{{ "%.6f"|format(fire.lng) }}</td>\n'
        '                    <td>{{ "%.6f"|format(fire.lat) }}</td>\n'
        '                    <td>{{ fire.acq_date }}</td>\n'
        '                </tr>\n'
        '                {% endfor %}\n'
        '            </tbody>\n'
        '        </table>\n'
        '    </div>\n'
        '\n'
        '    <script>\n'
        '        const map = new T.Map("map");\n'
        '        map.centerAndZoom(new T.LngLat(105, 35), 4);\n'
        '\n'
        '        const fires = {{ fire_data|tojson|safe }};\n'
        '        fires.forEach(fire => {\n'
        '            if (fire.lat && fire.lng) {\n'
        '                // 创建红色圆点\n'
        '                const circle = new T.CircleMarker(\n'
        '                    new T.LngLat(fire.lng, fire.lat),\n'
        '                    {\n'
        '                        radius: 6,\n'
        '                        fillColor: "#dc3545",\n'
        '                        color: "#fff",\n'
        '                        weight: 1,\n'
        '                        opacity: 1,\n'
        '                        fillOpacity: 0.9\n'
        '                    }\n'
        '                );\n'
        '\n'
        '                // 绑定点击弹窗\n'
        '                circle.bindInfoWindow(`\n'
        '                    <b>🔴 火点详情</b><br>\n'
        '                    经度: ${fire.lng.toFixed(6)}<br>\n'
        '                    纬度: ${fire.lat.toFixed(6)}<br>\n'
        '                    时间: ${fire.acq_date}\n'
        '                `);\n'
        '\n'
        '                // 添加到地图\n'
        '                map.addOverLay(circle);\n'
        '\n'
        '                // 添加脉冲动画（通过操作 DOM）\n'
        '                setTimeout(() => {\n'
        '                    const el = circle.getElement();\n'
        '                    if (el && el.firstChild) {\n'
        '                        el.firstChild.classList.add("pulse-circle");\n'
        '                    }\n'
        '                }, 100);\n'
        '            }\n'
        '        });\n'
        '    </script>\n'
        '</body>\n'
        '</html>'
    )

    return render_template_string(
        HTML,
        app_name=APP_NAME,
        tianditu_key=TIANDITU_KEY,
        fire_data=fire_list,
        fire_count=len(fire_list)
    )


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NASA 火点监测系统（测试版）启动成功！")
    print("🌐 访问: http://localhost:5000")
    print("📍 红色圆点 | 脉冲动画 | 居中缩小地图 | 美化数据面板")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)