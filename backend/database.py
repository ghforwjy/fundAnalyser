"""
数据库连接管理模块
使用fundData skill的SQLite数据库
"""
import sqlite3
import os
from contextlib import contextmanager

# 使用fundData skill的数据库
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                       ".trae", "skills", "fundData", "fund_data.db")


@contextmanager
def get_db_connection():
    """
    获取数据库连接的上下文管理器
    连接到fundData skill的SQLite数据库
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_portfolio_tables():
    """
    初始化投资组合相关表
    这些表在fundData数据库中已存在，无需重复创建
    portfolio, portfolio_fund, holding_history
    """
    # fundData skill已包含这些表，无需初始化
    print("[database] 投资组合表由fundData skill管理，跳过初始化")


def init_datasource_table():
    """
    初始化数据源配置表
    简化版本，仅保留基本配置
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_source_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name VARCHAR(50) UNIQUE NOT NULL,
                source_type VARCHAR(20) NOT NULL,
                description VARCHAR(200),
                is_active BOOLEAN DEFAULT 1,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 插入默认配置
        cursor.execute('''
            INSERT OR IGNORE INTO data_source_config 
            (source_name, source_type, description, is_active)
            VALUES 
            ('akshare', 'free', 'AKShare开源数据源', 1)
        ''')
        conn.commit()
        print("[database] 数据源配置表初始化完成")


def get_table_stats():
    """获取数据库表统计信息"""
    tables = [
        'fund_info', 'fund_nav', 'fund_stock_holding', 'fund_rating',
        'fund_manager', 'fund_company', 'portfolio', 'portfolio_fund'
    ]
    
    stats = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                stats[table] = count
            except:
                stats[table] = 0
    
    return stats
