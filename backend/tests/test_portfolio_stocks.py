"""
查询基金组合成分股和成分股各方面信息的测试脚本

功能：
1. 查询指定组合的所有成分基金
2. 查询每只基金的股票持仓（成分股）
3. 查询成分股的各方面信息（如市值、占净值比等）
4. 汇总分析组合的整体持仓情况
"""

import sys
sys.path.insert(0, '..')

from database import get_db_connection
from typing import List, Dict, Any, Optional
from datetime import datetime


class PortfolioStockAnalyzer:
    """组合成分股分析器"""

    def __init__(self):
        self.db_path = "../fund.db"

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """获取所有基金组合/分组"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.*, COUNT(m.id) as fund_count
                FROM fund_groups g
                LEFT JOIN fund_group_members m ON g.id = m.group_id
                GROUP BY g.id
                ORDER BY g.sort_order, g.create_time
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_group_funds(self, group_id: int) -> List[Dict[str, Any]]:
        """获取组合中的所有基金"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    m.fund_code,
                    f.fund_name,
                    f.fund_type,
                    f.company_name,
                    m.notes as fund_notes,
                    m.create_time as added_time
                FROM fund_group_members m
                JOIN fund_info f ON m.fund_code = f.fund_code
                WHERE m.group_id = ?
                ORDER BY m.create_time DESC
            """, (group_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_fund_stock_holdings(self, fund_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取基金最新的股票持仓（成分股）

        返回每只股票的：
        - 股票代码
        - 股票名称（如有）
        - 持仓市值
        - 持仓股数
        - 占净值比例
        - 报告期
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

