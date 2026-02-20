"""筛选选项API - 从fundData skill数据库查询"""
from fastapi import APIRouter
from database import get_db_connection

router = APIRouter(prefix="/api/filters", tags=["筛选选项"])


@router.get("/fund-types")
async def get_fund_types():
    """获取所有基金类型"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT fund_type 
                FROM fund_info 
                WHERE fund_type IS NOT NULL AND fund_type != '' 
                ORDER BY fund_type
            """)
            types = [row["fund_type"] for row in cursor.fetchall()]
            return {"success": True, "data": types}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


@router.get("/companies")
async def get_companies():
    """获取所有基金公司"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT company_name 
                FROM fund_info 
                WHERE company_name IS NOT NULL AND company_name != '' 
                ORDER BY company_name
            """)
            companies = [row["company_name"] for row in cursor.fetchall()]
            return {"success": True, "data": companies}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


@router.get("/managers")
async def get_managers():
    """获取所有基金经理"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT manager_name 
                FROM fund_manager 
                WHERE manager_name IS NOT NULL AND manager_name != '' 
                ORDER BY manager_name
            """)
            managers = [row["manager_name"] for row in cursor.fetchall()]
            return {"success": True, "data": managers}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}
