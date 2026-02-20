"""基金相关API - 从fundData skill数据库查询"""
from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/api/funds", tags=["基金"])


# ==================== 标签管理数据模型 ====================

class TagCreate(BaseModel):
    name: str
    category: Optional[str] = None
    color: Optional[str] = "#3b82f6"


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None


class FundTagsUpdate(BaseModel):
    tag_ids: List[int]


@router.get("")
async def get_funds(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fund_type: Optional[str] = None,
    company_name: Optional[str] = None,
    keyword: Optional[str] = None,
    order_by: str = "fund_code",
    order_dir: str = "ASC"
):
    """获取基金列表（支持筛选和搜索）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if fund_type:
                conditions.append("fund_type = ?")
                params.append(fund_type)
            
            if company_name:
                conditions.append("company_name = ?")
                params.append(company_name)
            
            if keyword:
                conditions.append("(fund_code LIKE ? OR fund_name LIKE ? OR pinyin_abbr LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # 获取总数
            count_sql = f"SELECT COUNT(*) as count FROM fund_info {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["count"]
            
            # 获取分页数据
            offset = (page - 1) * page_size
            order_dir = "DESC" if order_dir.upper() == "DESC" else "ASC"
            
            # 查询fundData数据库的fund_info表
            data_sql = f"""
                SELECT 
                    fi.fund_code,
                    fi.fund_name,
                    fi.fund_full_name,
                    fi.fund_type,
                    fi.pinyin_abbr,
                    fi.pinyin_full,
                    fi.company_name,
                    fi.custodian,
                    fi.issue_date,
                    fi.establish_date,
                    fi.establish_scale,
                    fi.manage_fee_rate,
                    fi.custodian_fee_rate,
                    fi.benchmark,
                    fi.invest_scope,
                    fi.track_target,
                    fi.status,
                    fn.unit_nav as latest_nav,
                    fn.nav_date
                FROM fund_info fi
                LEFT JOIN (
                    SELECT fund_code, unit_nav, nav_date
                    FROM fund_nav
                    WHERE (fund_code, nav_date) IN (
                        SELECT fund_code, MAX(nav_date)
                        FROM fund_nav
                        GROUP BY fund_code
                    )
                ) fn ON fi.fund_code = fn.fund_code
                {where_clause}
                ORDER BY fi.{order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_sql, params + [page_size, offset])
            rows = cursor.fetchall()
            
            # 转换为字典列表
            funds = []
            for row in rows:
                funds.append({
                    "fund_code": row["fund_code"],
                    "fund_name": row["fund_name"],
                    "fund_full_name": row["fund_full_name"],
                    "fund_type": row["fund_type"],
                    "pinyin_abbr": row["pinyin_abbr"],
                    "pinyin_full": row["pinyin_full"],
                    "company_name": row["company_name"],
                    "custodian": row["custodian"],
                    "issue_date": row["issue_date"],
                    "establish_date": row["establish_date"],
                    "establish_scale": row["establish_scale"],
                    "manage_fee_rate": row["manage_fee_rate"],
                    "custodian_fee_rate": row["custodian_fee_rate"],
                    "benchmark": row["benchmark"],
                    "invest_scope": row["invest_scope"],
                    "track_target": row["track_target"],
                    "status": row["status"],
                    "latest_nav": row["latest_nav"],
                    "nav_date": row["nav_date"]
                })
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "success": True, 
                "data": {
                    "data": funds,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@router.get("/{fund_code}")
async def get_fund_detail(fund_code: str):
    """获取基金详情"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 查询基金基本信息
            cursor.execute("""
                SELECT fi.*, 
                       fn.unit_nav as latest_nav,
                       fn.accum_nav as latest_accum_nav,
                       fn.nav_date
                FROM fund_info fi
                LEFT JOIN (
                    SELECT fund_code, unit_nav, accum_nav, nav_date
                    FROM fund_nav
                    WHERE (fund_code, nav_date) IN (
                        SELECT fund_code, MAX(nav_date)
                        FROM fund_nav
                        WHERE fund_code = ?
                    )
                ) fn ON fi.fund_code = fn.fund_code
                WHERE fi.fund_code = ?
            """, (fund_code, fund_code))
            
            row = cursor.fetchone()
            if row:
                fund_data = dict(row)
                
                # 查询风险指标
                cursor.execute("""
                    SELECT period, sharpe_ratio, max_drawdown, annual_volatility,
                           risk_return_ratio, risk_resistance
                    FROM fund_risk_metrics
                    WHERE fund_code = ?
                    ORDER BY period
                """, (fund_code,))
                risk_metrics = [dict(r) for r in cursor.fetchall()]
                fund_data['risk_metrics'] = risk_metrics
                
                # 查询基金评级
                cursor.execute("""
                    SELECT rating_sh, rating_zs, rating_ja, rating_morningstar,
                           rating_5star_count
                    FROM fund_rating
                    WHERE fund_code = ?
                """, (fund_code,))
                rating_row = cursor.fetchone()
                if rating_row:
                    fund_data['rating'] = dict(rating_row)
                
                return {"success": True, "data": fund_data}
            else:
                raise HTTPException(status_code=404, detail="基金不存在")
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@router.get("/{fund_code}/nav")
async def get_fund_nav(
    fund_code: str, 
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取基金净值历史"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT fund_code, nav_date, unit_nav, accum_nav, daily_return
                FROM fund_nav 
                WHERE fund_code = ?
            """
            params = [fund_code]
            
            if start_date:
                query += " AND nav_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND nav_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY nav_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            nav_data = [dict(row) for row in rows]
            
            return {"success": True, "data": {"nav": nav_data}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@router.get("/{fund_code}/holdings")
async def get_fund_holdings(
    fund_code: str, 
    report_date: Optional[str] = None,
    year: Optional[str] = None
):
    """获取基金持仓"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 如果没有指定年份，使用当前年份
            if not year and not report_date:
                from datetime import datetime
                year = str(datetime.now().year)
            
            if report_date:
                # 按具体报告日期查询
                cursor.execute("""
                    SELECT stock_code, stock_name, hold_ratio, hold_shares, 
                           hold_value, quarter
                    FROM fund_stock_holding 
                    WHERE fund_code = ? AND report_date = ?
                    ORDER BY hold_ratio DESC
                """, (fund_code, report_date))
            else:
                # 按年份查询最新的报告期
                cursor.execute("""
                    SELECT stock_code, stock_name, hold_ratio, hold_shares,
                           hold_value, quarter, report_date
                    FROM fund_stock_holding 
                    WHERE fund_code = ? AND quarter LIKE ?
                    ORDER BY report_date DESC, hold_ratio DESC
                    LIMIT 50
                """, (fund_code, f"%{year}%"))
            
            rows = cursor.fetchall()
            holdings = [dict(row) for row in rows]
            
            return {"success": True, "data": holdings}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@router.get("/{fund_code}/industry")
async def get_fund_industry_allocation(
    fund_code: str,
    year: Optional[str] = None
):
    """获取基金行业配置"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if not year:
                from datetime import datetime
                year = str(datetime.now().year)
            
            cursor.execute("""
                SELECT industry_name, allocation_ratio, market_value, quarter
                FROM fund_industry_allocation
                WHERE fund_code = ? AND quarter LIKE ?
                ORDER BY report_date DESC, allocation_ratio DESC
            """, (fund_code, f"%{year}%"))
            
            rows = cursor.fetchall()
            industries = [dict(row) for row in rows]
            
            return {"success": True, "data": industries}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@router.get("/{fund_code}/performance")
async def get_fund_performance(fund_code: str):
    """获取基金业绩表现"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT performance_type, period, period_return, max_drawdown, rank_in_category
                FROM fund_performance
                WHERE fund_code = ?
                ORDER BY performance_type, period
            """, (fund_code,))
            
            rows = cursor.fetchall()
            performance = [dict(row) for row in rows]
            
            return {"success": True, "data": performance}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


# ==================== 标签管理API ====================

@router.get("/tags/all")
async def get_all_tags(category: Optional[str] = None):
    """获取所有标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import get_all_tags
        tags = get_all_tags(category)
        return {"success": True, "data": tags}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/tags/search")
async def search_tags(keyword: str = Query(..., min_length=1)):
    """模糊搜索标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import search_tags
        tags = search_tags(keyword)
        return {"success": True, "data": tags}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/tags/categories")
async def get_tag_categories():
    """获取所有标签分类"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import get_tag_categories
        categories = get_tag_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/tags")
async def create_tag(data: TagCreate):
    """创建新标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import create_tag
        result = create_tag(data.name, data.category, data.color)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/tags/{tag_id}")
async def update_tag(tag_id: int, data: TagUpdate):
    """更新标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import update_tag
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        result = update_tag(tag_id, **fields)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int):
    """删除标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import delete_tag
        result = delete_tag(tag_id)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 基金标签关联API ====================

@router.get("/{fund_code}/tags")
async def get_fund_tags(fund_code: str):
    """获取基金的标签列表"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import get_fund_tags
        tags = get_fund_tags(fund_code)
        return {"success": True, "data": tags}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/{fund_code}/tags")
async def set_fund_tags(fund_code: str, data: FundTagsUpdate):
    """批量设置基金标签（覆盖式）"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import set_fund_tags
        result = set_fund_tags(fund_code, data.tag_ids)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/{fund_code}/tags/{tag_id}")
async def add_fund_tag(fund_code: str, tag_id: int):
    """给基金添加单个标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import add_fund_tag
        result = add_fund_tag(fund_code, tag_id)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.delete("/{fund_code}/tags/{tag_id}")
async def remove_fund_tag(fund_code: str, tag_id: int):
    """移除基金的单个标签"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        from tag_manager import remove_fund_tag
        result = remove_fund_tag(fund_code, tag_id)
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}
