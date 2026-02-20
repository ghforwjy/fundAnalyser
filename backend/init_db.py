"""
数据库初始化脚本
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_datasource_table, init_portfolio_tables, init_global_data_tables, init_group_data_tables, init_all_tables

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fund.db")
SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "fund_database_create.sql")

def init_database():
    """初始化数据库"""
    print(f"正在初始化数据库: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        print("数据库已存在，将添加新表...")
    else:
        print("创建新数据库...")
        conn = sqlite3.connect(DB_PATH)
        conn.close()
    
    print("\n初始化数据源配置表...")
    init_datasource_table()
    
    print("\n初始化投资组合表...")
    init_portfolio_tables()
    
    print("\n初始化全局数据表...")
    init_global_data_tables()
    
    print("\n初始化分组数据表...")
    init_group_data_tables()
    
    print("\n数据库初始化完成！")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\n已创建 {len(tables)} 个表:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} 条记录")
    conn.close()

def init_database_from_sql():
    """从SQL脚本初始化数据库（旧方法，保留备用）"""
    print(f"正在从SQL脚本初始化数据库: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("已删除旧数据库")
    
    conn = sqlite3.connect(DB_PATH)
    
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    conn.executescript(sql_script)
    conn.commit()
    conn.close()
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_database()
