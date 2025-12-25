#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NASA FIRMS 火点数据采集器 - 兼容现有表结构版
兼容现有的 fire_points 表结构 (id, lat, lng, time)
"""

import sys
import csv
import io
import requests
import pymysql
import time
from datetime import datetime, timezone, timedelta

# ===== 配置 =====
NASA_API_KEY = "1XLOxwvWIqcKytXrJUYr7fbor4BIWIN2X9c8IZS0"
COUNTRY_CODE = "CHN"

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'fire_monitoring',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def print_log(message, level="INFO"):
    """简单的日志打印"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {level} - {message}")

def check_database():
    """检查数据库连接和表结构"""
    try:
        print_log("检查数据库连接...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'fire_points'")
        if not cursor.fetchone():
            print_log("表 fire_points 不存在，创建新表...", "WARN")
            # 创建简单表
            create_sql = """
            CREATE TABLE fire_points (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat FLOAT NOT NULL,
                lng FLOAT NOT NULL,
                time TIMESTAMP NOT NULL,
                UNIQUE KEY unique_location_time (lat, lng, time)
            )
            """
            cursor.execute(create_sql)
            conn.commit()
            print_log("表创建成功")
        else:
            # 检查表结构
            cursor.execute("DESCRIBE fire_points")
            columns = cursor.fetchall()
            print_log("表结构:")
            for col in columns:
                print_log(f"  {col['Field']}: {col['Type']} ({'NOT NULL' if col['Null'] == 'NO' else 'NULL'})")
        
        # 检查现有数据量
        cursor.execute("SELECT COUNT(*) as count FROM fire_points")
        count = cursor.fetchone()['count']
        print_log(f"现有数据量: {count} 条")
        
        # 检查最新数据日期
        cursor.execute("SELECT MAX(time) as latest FROM fire_points")
        latest = cursor.fetchone()['latest']
        if latest:
            print_log(f"最新数据时间: {latest}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_log(f"数据库错误: {str(e)}", "ERROR")
        print_log("请检查数据库配置和连接", "ERROR")
        return False

def test_nasa_api():
    """测试NASA API连接"""
    print_log("测试NASA API连接...")
    
    # 测试不同日期，确保能获取数据
    test_dates = [
        (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d"),  # 一周前
        '2025-12-15',
        '2025-12-10'
    ]
    
    for test_date in test_dates:
        try:
            url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"
            params = {
                'country': COUNTRY_CODE,
                'date': test_date,
                'api_key': NASA_API_KEY,
                'source': 'VIIRS_SNPP_NRT',
                'fmt': 'csv'
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                content = response.text.strip()
                if content and "error" not in content.lower():
                    # 尝试解析CSV
                    reader = csv.DictReader(io.StringIO(content))
                    records = list(reader)
                    
                    if records:
                        print_log(f"API测试成功! {test_date}: 获取到 {len(records)} 条记录", "SUCCESS")
                        print_log(f"样例记录字段: {list(records[0].keys())}")
                        return True, test_date
                    else:
                        print_log(f"{test_date}: 响应无有效记录")
                else:
                    print_log(f"{test_date}: 响应为空或包含错误")
            else:
                print_log(f"{test_date}: HTTP {response.status_code}")
                
        except Exception as e:
            print_log(f"{test_date} 请求失败: {str(e)}")
    
    print_log("所有测试日期都无数据，但API可能有效", "WARN")
    return True, None

def get_query_dates():
    """获取要查询的日期范围"""
    now_utc = datetime.now(timezone.utc)
    
    # 考虑到NASA数据延迟，查询5-10天前的数据
    dates = []
    for days_ago in range(5, 11):  # 5-10天前
        date = (now_utc - timedelta(days=days_ago)).date()
        dates.append(date.strftime("%Y-%m-%d"))
    
    print_log(f"将查询以下日期: {', '.join(dates)}")
    return dates

def fetch_data_for_date(date_str):
    """获取指定日期的火点数据"""
    print_log(f"获取 {date_str} 数据...")
    
    # 数据源列表
    sources = [
        ('VIIRS_SNPP_NRT', 'VIIRS SNPP'),
        ('VIIRS_NOAA20_NRT', 'VIIRS NOAA20'),
        ('MODIS_NRT', 'MODIS'),
        ('VIIRS_SNPP_SP', 'VIIRS SNPP标准'),
    ]
    
    all_records = []
    
    for source, source_name in sources:
        try:
            url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"
            params = {
                'country': COUNTRY_CODE,
                'date': date_str,
                'api_key': NASA_API_KEY,
                'source': source,
                'fmt': 'csv'
            }
            
            response = requests.get(url, params=params, timeout=25)
            
            if response.status_code == 200:
                content = response.text.strip()
                
                if not content:
                    continue
                    
                if "error" in content.lower():
                    continue
                
                # 解析CSV数据
                try:
                    reader = csv.DictReader(io.StringIO(content))
                    records = []
                    
                    for row in reader:
                        if 'latitude' in row and 'longitude' in row and 'acq_date' in row:
                            # 只保留需要的字段
                            record = {
                                'lat': row['latitude'],
                                'lng': row['longitude'],
                                'acq_date': row['acq_date'],
                                'acq_time': row.get('acq_time', '0000'),
                                'satellite': row.get('satellite', ''),
                                'data_source': source
                            }
                            records.append(record)
                    
                    if records:
                        print_log(f"  {source_name}: {len(records)} 条", "SUCCESS")
                        all_records.extend(records)
                        
                except Exception as e:
                    print_log(f"  解析CSV失败: {str(e)}", "DEBUG")
                    
            time.sleep(0.5)  # 避免请求过快
            
        except requests.exceptions.Timeout:
            print_log(f"  {source_name}: 超时", "WARN")
        except Exception as e:
            print_log(f"  {source_name}: 错误 {str(e)}", "DEBUG")
    
    if all_records:
        print_log(f"{date_str}: 总共获取 {len(all_records)} 条记录", "SUCCESS")
    else:
        print_log(f"{date_str}: 无数据", "INFO")
    
    return all_records

def save_to_database(records):
    """保存数据到数据库"""
    if not records:
        return 0, 0
    
    total = len(records)
    inserted = 0
    skipped = 0
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for i, record in enumerate(records, 1):
            try:
                # 提取数据
                lat = float(record['lat'])
                lng = float(record['lng'])
                acq_date = record['acq_date']
                acq_time = record.get('acq_time', '0000')
                
                # 构建时间戳 (使用acq_date的中午时间，因为原表只有一个time字段)
                # 格式: YYYY-MM-DD HH:MM:SS
                hour = int(acq_time[:2]) if len(acq_time) >= 2 else 12
                minute = int(acq_time[2:4]) if len(acq_time) >= 4 else 0
                time_str = f"{acq_date} {hour:02d}:{minute:02d}:00"
                
                # 插入数据 (使用 INSERT IGNORE 避免重复)
                sql = """
                INSERT IGNORE INTO fire_points (lat, lng, time) 
                VALUES (%s, %s, %s)
                """
                
                cursor.execute(sql, (lat, lng, time_str))
                
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
                
                # 每100条提交一次
                if i % 100 == 0:
                    conn.commit()
                    
            except Exception as e:
                print_log(f"处理记录失败: {str(e)}", "DEBUG")
                skipped += 1
        
        conn.commit()
        conn.close()
        
        print_log(f"保存完成: 新增 {inserted} 条，跳过 {skipped} 条", "SUCCESS")
        return inserted, skipped
        
    except Exception as e:
        print_log(f"数据库保存失败: {str(e)}", "ERROR")
        return 0, total

def main():
    """主程序"""
    print("=" * 60)
    print("NASA FIRMS 火点数据采集器")
    print("=" * 60)
    
    # 1. 检查数据库
    if not check_database():
        print_log("数据库检查失败，程序退出", "ERROR")
        return
    
    # 2. 测试API
    api_ok, test_date = test_nasa_api()
    if not api_ok:
        print_log("API测试失败，程序退出", "ERROR")
        return
    
    # 3. 获取查询日期
    dates = get_query_dates()
    
    # 4. 收集数据
    all_records = []
    
    print_log("开始收集数据...")
    for date in dates:
        records = fetch_data_for_date(date)
        if records:
            all_records.extend(records)
    
    print_log(f"数据收集完成，总共获取 {len(all_records)} 条记录")
    
    if not all_records:
        print_log("未获取到任何数据，可能原因:", "WARN")
        print_log("  1. 查询日期范围内确实没有火点", "WARN")
        print_log("  2. NASA数据延迟（尝试更早的日期）", "WARN")
        print_log("  3. API限制或服务器问题", "WARN")
        print_log("建议:", "WARN")
        print_log("  1. 等待几天再尝试", "WARN")
        print_log("  2. 手动测试API: ", "WARN")
        print_log(f'    curl "https://firms.modaps.eosdis.nasa.gov/api/country/csv/{COUNTRY_CODE}/2025-12-10/{NASA_API_KEY}/VIIRS_SNPP_NRT"', "WARN")
        return
    
    # 5. 去重（基于位置和日期）
    unique_records = []
    seen = set()
    
    for record in all_records:
        # 使用位置和日期作为唯一标识
        key = (record['lat'], record['lng'], record['acq_date'])
        if key not in seen:
            seen.add(key)
            unique_records.append(record)
    
    print_log(f"去重后剩余 {len(unique_records)} 条唯一记录")
    
    # 6. 保存到数据库
    inserted, skipped = save_to_database(unique_records)
    
    print("=" * 60)
    print("采集结果:")
    print(f"  查询日期: {len(dates)} 天")
    print(f"  获取记录: {len(all_records)} 条")
    print(f"  唯一记录: {len(unique_records)} 条")
    print(f"  新增入库: {inserted} 条")
    print(f"  跳过重复: {skipped} 条")
    print("=" * 60)
    
    if inserted == 0:
        print_log("没有新增数据，可能所有记录已存在", "INFO")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_log("用户中断程序", "INFO")
    except Exception as e:
        print_log(f"程序异常: {str(e)}", "ERROR")