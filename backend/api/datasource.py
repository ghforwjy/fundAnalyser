"""数据源配置API - 简化版本（仅保留查询功能）"""
from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(prefix="/api/datasource", tags=["数据源"])


@router.get("")
async def get_data_sources():
    """获取数据源信息（仅显示，不再管理同步）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 获取fundData数据库统计信息
            cursor.execute("SELECT COUNT(*) as count FROM fund_info")
            fund_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM fund_nav")
            nav_count = cursor.fetchone()["count"]
            
            # 返回简化的数据源信息
            data_sources = [
                {
                    "id": 1,
                    "source_name": "fundData_skill",
                    "source_type": "local_sqlite",
                    "description": "fundData skill本地SQLite数据库",
                    "is_active": True,
                    "is_connected": True,
                    "fund_count": fund_count,
                    "nav_count": nav_count,
                    "note": "数据由fundData skill维护，本项目仅查询使用"
                }
            ]
            return {"success": True, "data": data_sources}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


@router.get("/stats")
async def get_data_stats():
    """获取数据统计信息"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 基金统计
            cursor.execute("SELECT COUNT(*) as count FROM fund_info")
            stats["total_funds"] = cursor.fetchone()["count"]
            
            # 净值统计
            cursor.execute("SELECT COUNT(*) as count FROM fund_nav")
            stats["total_nav_records"] = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(DISTINCT fund_code) as count FROM fund_nav")
            stats["nav_coverage"] = cursor.fetchone()["count"]
            
            # 持仓统计
            cursor.execute("SELECT COUNT(*) as count FROM fund_stock_holding")
            stats["stock_holdings"] = cursor.fetchone()["count"]
            
            # 组合统计
            cursor.execute("SELECT COUNT(*) as count FROM portfolio")
            stats["total_portfolios"] = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM portfolio_fund")
            stats["total_portfolio_funds"] = cursor.fetchone()["count"]
            
            return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
