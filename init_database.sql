
CREATE DATABASE IF NOT EXISTS fire_monitoring DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE fire_monitoring;

-- 火点事件表
CREATE TABLE IF NOT EXISTS fire_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DECIMAL(9, 6) NOT NULL COMMENT '纬度',
    longitude DECIMAL(9, 6) NOT NULL COMMENT '经度',
    acquisition_date DATE NOT NULL COMMENT '探测日期',
    acquisition_time TIME NOT NULL COMMENT '探测时间',
    acquisition_datetime DATETIME GENERATED ALWAYS AS (CONCAT(acquisition_date, ' ', acquisition_time)) STORED COMMENT '完整探测时间',
    confidence VARCHAR(20) COMMENT '置信度',
    satellite VARCHAR(20) NOT NULL COMMENT '卫星来源',
    bright_ti4 DECIMAL(8, 2) COMMENT '亮度温度(K)',
    frp DECIMAL(8, 2) COMMENT '火辐射功率(MW)',
    geometry_point POINT NOT NULL SRID 4326 COMMENT '空间几何点',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    SPATIAL INDEX idx_geometry (geometry_point),
    INDEX idx_acquisition (acquisition_datetime),
    INDEX idx_satellite (satellite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- API日志表
CREATE TABLE IF NOT EXISTS api_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_endpoint VARCHAR(500) NOT NULL,
    response_size INT DEFAULT 0,
    record_count INT DEFAULT 0,
    status_code INT,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 系统状态表
CREATE TABLE IF NOT EXISTS system_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component VARCHAR(50) NOT NULL COMMENT '组件名称',
    status VARCHAR(20) NOT NULL COMMENT '状态(running, stopped, error)',
    last_run TIMESTAMP NULL,
    next_run TIMESTAMP NULL,
    message TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
