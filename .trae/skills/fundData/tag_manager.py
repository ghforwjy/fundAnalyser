"""
基金标签管理模块
提供基金标签的CRUD和基金标签关联管理
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fund_data.db")


@dataclass
class Tag:
    """标签数据类"""
    id: int
    name: str
    category: Optional[str] = None
    color: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None


@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_tag_tables():
    """初始化标签相关表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                category VARCHAR(50),
                color VARCHAR(20) DEFAULT '#3b82f6',
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 基金标签关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_tag_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code VARCHAR(10) NOT NULL,
                tag_id INTEGER NOT NULL,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, tag_id),
                FOREIGN KEY (tag_id) REFERENCES fund_tags(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tag_relations_fund ON fund_tag_relations(fund_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tag_relations_tag ON fund_tag_relations(tag_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_category ON fund_tags(category)')
        
        conn.commit()
        print("[TagManager] 标签表初始化完成")


# ==================== 标签管理 ====================

def create_tag(name: str, category: Optional[str] = None, color: Optional[str] = None) -> Dict[str, Any]:
    """创建新标签"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fund_tags (name, category, color, update_time)
                VALUES (?, ?, ?, datetime('now'))
            ''', (name, category, color or '#3b82f6'))
            conn.commit()
            tag_id = cursor.lastrowid
            return {'success': True, 'data': {'id': tag_id, 'name': name, 'category': category, 'color': color}}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': f'标签 "{name}" 已存在'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def update_tag(tag_id: int, **fields) -> Dict[str, Any]:
    """更新标签信息"""
    allowed_fields = ['name', 'category', 'color']
    updates = []
    params = []
    
    for key, value in fields.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(value)
    
    if not updates:
        return {'success': False, 'error': '没有可更新的字段'}
    
    updates.append("update_time = datetime('now')")
    params.append(tag_id)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = f"UPDATE fund_tags SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
            if cursor.rowcount > 0:
                return {'success': True, 'message': '更新成功'}
            else:
                return {'success': False, 'error': '标签不存在'}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': '标签名称已存在'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def delete_tag(tag_id: int) -> Dict[str, Any]:
    """删除标签（会自动删除关联关系）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fund_tags WHERE id = ?", (tag_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {'success': True, 'message': '删除成功'}
            else:
                return {'success': False, 'error': '标签不存在'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_all_tags(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取所有标签"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('''
                    SELECT id, name, category, color, create_time, update_time
                    FROM fund_tags WHERE category = ? ORDER BY name
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT id, name, category, color, create_time, update_time
                    FROM fund_tags ORDER BY category, name
                ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"[TagManager] 获取标签列表失败: {e}")
        return []


def search_tags(keyword: str) -> List[Dict[str, Any]]:
    """模糊搜索标签"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, color, create_time, update_time
                FROM fund_tags 
                WHERE name LIKE ? OR category LIKE ?
                ORDER BY name
            ''', (f'%{keyword}%', f'%{keyword}%'))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"[TagManager] 搜索标签失败: {e}")
        return []


def get_tag_categories() -> List[str]:
    """获取所有标签分类"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT category FROM fund_tags 
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            ''')
            rows = cursor.fetchall()
            return [row[0] for row in rows if row[0]]
    except Exception as e:
        print(f"[TagManager] 获取标签分类失败: {e}")
        return []


# ==================== 基金标签关联管理 ====================

def get_fund_tags(fund_code: str) -> List[Dict[str, Any]]:
    """获取基金的标签列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.name, t.category, t.color, r.create_time as tagged_time
                FROM fund_tags t
                JOIN fund_tag_relations r ON t.id = r.tag_id
                WHERE r.fund_code = ?
                ORDER BY t.category, t.name
            ''', (fund_code,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"[TagManager] 获取基金标签失败: {e}")
        return []


def add_fund_tag(fund_code: str, tag_id: int) -> Dict[str, Any]:
    """给基金添加标签"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO fund_tag_relations (fund_code, tag_id)
                VALUES (?, ?)
            ''', (fund_code, tag_id))
            conn.commit()
            return {'success': True, 'message': '添加成功'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def remove_fund_tag(fund_code: str, tag_id: int) -> Dict[str, Any]:
    """移除基金的标签"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM fund_tag_relations 
                WHERE fund_code = ? AND tag_id = ?
            ''', (fund_code, tag_id))
            conn.commit()
            return {'success': True, 'message': '移除成功'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def set_fund_tags(fund_code: str, tag_ids: List[int]) -> Dict[str, Any]:
    """批量设置基金标签（覆盖式）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 删除现有标签关联
            cursor.execute("DELETE FROM fund_tag_relations WHERE fund_code = ?", (fund_code,))
            
            # 添加新标签关联
            for tag_id in tag_ids:
                cursor.execute('''
                    INSERT INTO fund_tag_relations (fund_code, tag_id)
                    VALUES (?, ?)
                ''', (fund_code, tag_id))
            
            conn.commit()
            return {'success': True, 'message': '设置成功'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_funds_by_tag(tag_id: int) -> List[str]:
    """获取拥有指定标签的所有基金代码"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fund_code FROM fund_tag_relations 
                WHERE tag_id = ?
            ''', (tag_id,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        print(f"[TagManager] 获取标签基金列表失败: {e}")
        return []


def get_all_fund_tags() -> Dict[str, List[Dict[str, Any]]]:
    """获取所有基金的标签映射"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.fund_code, t.id, t.name, t.category, t.color
                FROM fund_tag_relations r
                JOIN fund_tags t ON r.tag_id = t.id
                ORDER BY r.fund_code, t.name
            ''')
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                fund_code = row['fund_code']
                if fund_code not in result:
                    result[fund_code] = []
                result[fund_code].append({
                    'id': row['id'],
                    'name': row['name'],
                    'category': row['category'],
                    'color': row['color']
                })
            return result
    except Exception as e:
        print(f"[TagManager] 获取所有基金标签失败: {e}")
        return {}


# 初始化表结构
if __name__ == '__main__':
    init_tag_tables()
