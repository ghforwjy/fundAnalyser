"""
配置文件
"""
from typing import Dict, Any

# 应用配置
APP_CONFIG = {
    "title": "基金数据平台 API",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000
}

# 数据库配置
DB_CONFIG = {
    "path": "../fund.db"
}

# 数据源配置
DATA_SOURCE_CONFIG = {
    "akshare": {
        "name": "akshare",
        "type": "free",
        "description": "免费开源数据源",
        "rate_limit": 100,
        "is_active": True
    },
    "tushare": {
        "name": "tushare",
        "type": "paid",
        "description": "专业数据源",
        "rate_limit": 60,
        "is_active": False
    }
}

# 同步配置
SYNC_CONFIG = {
    "fund_info": {
        "table": "fund_info",
        "description": "基金基本信息",
        "sync_type": "full",  # full: 全量, incremental: 增量
        "batch_size": 100
    },
    "fund_nav": {
        "table": "fund_nav",
        "description": "基金净值",
        "sync_type": "incremental",
        "batch_size": 500
    },
    "fund_stock_holding": {
        "table": "fund_stock_holding",
        "description": "基金股票持仓",
        "sync_type": "incremental",
        "batch_size": 100
    },
    "fund_manager": {
        "table": "fund_manager",
        "description": "基金经理",
        "sync_type": "full",
        "batch_size": 100
    }
}

# CORS配置
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}