"""数据库管理API - 查询fundData skill数据库"""
from fastapi import APIRouter, Query
from typing import Optional
import sqlite3
import os

router = APIRouter(prefix="/api/db", tags=["数据库管理"])

# fundData skill数据库中的主要表
FUND_DATA_TABLES = [
    'fund_info', 'fund_nav', 'fund_stock_holding', 'fund_bond_holding',
    'fund_industry_allocation', 'fund_risk_metrics', 'fund_performance',
    'fund_rating', 'fund_manager', 'fund_company', 'fund_dividend',
    'fund_split', 'fund_rank', 'fund_purchase_status',
    'portfolio', 'portfolio_fund', 'holding_history'
]

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                       ".trae", "skills", "fundData", "fund_data.db")


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/tables")
async def get_tables():
    """获取数据库表列表"""
    try:
        print(f"[db_manage] 数据库路径: {DB_PATH}")
        print(f"[db_manage] 数据库是否存在: {os.path.exists(DB_PATH)}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        tables = []
        
        for table_name in FUND_DATA_TABLES:
            try:
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                record_count = cursor.fetchone()["count"]
                
                # 获取索引数
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                index_count = len(indexes)
                
                tables.append({
                    "table_name": table_name,
                    "index_count": index_count,
                    "record_count": record_count
                })
                print(f"[db_manage] 表 {table_name}: {record_count} 条记录, {index_count} 个索引")
            except Exception as e:
                # 表不存在则跳过
                print(f"[db_manage] 表 {table_name} 不存在或错误: {e}")
                pass
        
        conn.close()
        return {"success": True, "data": tables}
    except Exception as e:
        print(f"[db_manage] 获取表列表错误: {e}")
        return {"success": False, "message": str(e), "data": []}


@router.get("/tables/{table_name}")
async def get_table_schema(table_name: str):
    """获取表结构"""
    try:
        print(f"[db_manage] 获取表结构: {table_name}")
        print(f"[db_manage] 数据库路径: {DB_PATH}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取列信息
        cursor.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
        columns = []
        for row in rows:
            columns.append({
                "cid": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "notnull": row["notnull"],
                "dflt_value": row["dflt_value"],
                "pk": row["pk"]
            })
        
        print(f"[db_manage] 表 {table_name} 有 {len(columns)} 个字段")
        
        # 获取索引信息
        cursor.execute(f"PRAGMA index_list({table_name})")
        index_rows = cursor.fetchall()
        indexes = []
        for idx in index_rows:
            indexes.append({
                "seq": idx["seq"],
                "name": idx["name"],
                "unique": idx["unique"],
                "origin": idx["origin"] if "origin" in idx.keys() else "",
                "partial": idx["partial"] if "partial" in idx.keys() else 0
            })
        
        # 获取记录数
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            record_count = cursor.fetchone()["count"]
        except:
            record_count = 0
        
        # 获取外键信息
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fk_rows = cursor.fetchall()
        foreign_keys = []
        for fk in fk_rows:
            foreign_keys.append({
                "id": fk["id"],
                "seq": fk["seq"],
                "table": fk["table"],
                "from": fk["from"],
                "to": fk["to"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "table_name": table_name,
                "columns": columns,
                "indexes": indexes,
                "record_count": record_count,
                "foreign_keys": foreign_keys
            }
        }
    except Exception as e:
        print(f"[db_manage] 获取表结构错误: {e}")
        return {"success": False, "message": str(e), "data": None}


@router.get("/tables/{table_name}/data")
async def get_table_data(
    table_name: str, 
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_dir: str = "ASC"
):
    """获取表数据（支持后端搜索和排序）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表结构以确定列名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col["name"] for col in columns_info]
        
        # 构建搜索条件
        where_clause = ""
        params = []
        if search and column_names:
            # 只搜索文本类型的列
            text_columns = [col["name"] for col in columns_info 
                           if col["type"].upper() in ('TEXT', 'VARCHAR', 'CHAR', 'STRING')]
            if text_columns:
                search_conditions = [f"{col} LIKE ?" for col in text_columns]
                where_clause = "WHERE " + " OR ".join(search_conditions)
                search_param = f"%{search}%"
                params = [search_param] * len(text_columns)
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as count FROM {table_name} {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["count"]
        
        # 构建排序
        order_clause = ""
        if sort_field and sort_field in column_names:
            sort_dir = "DESC" if sort_dir.upper() == "DESC" else "ASC"
            order_clause = f"ORDER BY {sort_field} {sort_dir}"
        
        # 获取数据
        offset = (page - 1) * page_size
        data_sql = f"SELECT * FROM {table_name} {where_clause} {order_clause} LIMIT ? OFFSET ?"
        cursor.execute(data_sql, params + [page_size, offset])
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        conn.close()
        
        return {
            "success": True, 
            "data": {
                "data": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        print(f"[db_manage] 获取表数据错误: {e}")
        return {"success": False, "message": str(e), "data": None}
