"""
基金分组和持仓管理API - 使用fundData skill的组合功能
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from database import get_db_connection
from services.image_recognition_service import get_image_recognition_service

router = APIRouter(prefix="/api/portfolio", tags=["投资组合"])


# ==================== 数据模型 ====================

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AddFundToGroup(BaseModel):
    fund_code: str
    fund_name: Optional[str] = None
    shares: Optional[float] = None
    buy_date: Optional[str] = None
    buy_nav: Optional[float] = None
    amount: Optional[float] = None


class TransactionCreate(BaseModel):
    fund_code: str
    transaction_type: str  # BUY/SELL
    transaction_date: str
    shares: float
    price: float
    fee: Optional[float] = 0
    notes: Optional[str] = None


class ImageRecognitionRequest(BaseModel):
    image_base64: str


# ==================== 图片识别API ====================

@router.post("/recognize-image")
async def recognize_image(data: ImageRecognitionRequest):
    """识别基金持仓截图"""
    print(f"[后端] 收到图片识别请求，base64长度: {len(data.image_base64)}")
    try:
        service = get_image_recognition_service()
        print(f"[后端] 图片识别服务状态: 可用={service.is_available()}")
        result = service.recognize_fund_image(data.image_base64)
        print(f"[后端] 识别结果: success={result.get('success')}, 数据条数={len(result.get('data', []))}")
        return result
    except Exception as e:
        print(f"[后端] 识别异常: {str(e)}")
        return {"success": False, "data": [], "message": f"识别失败: {str(e)}"}


# ==================== 组合管理API ====================

@router.get("/groups")
async def get_groups():
    """获取所有组合（使用fundData的portfolio表）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, create_time, update_time,
                       (SELECT COUNT(*) FROM portfolio_fund WHERE portfolio_id = p.id) as fund_count
                FROM portfolio p
                ORDER BY create_time DESC
            """)
            rows = cursor.fetchall()
            groups = []
            for row in rows:
                groups.append({
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "fund_count": row["fund_count"],
                    "create_time": row["create_time"],
                    "update_time": row["update_time"]
                })
            return {"success": True, "data": groups}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 交易维护API ====================

class TransactionCreate(BaseModel):
    fund_code: str
    transaction_type: str  # BUY/SELL
    transaction_date: str
    shares: float
    amount: float
    nav: Optional[float] = None
    fee: Optional[float] = 0
    notes: Optional[str] = None


class ProfitImport(BaseModel):
    fund_code: str
    fund_name: Optional[str] = None
    profit_loss: float  # 盈亏金额（正数表示盈利，负数表示亏损）
    # current_value 不再由前端传入，后端自动计算：shares × latest_nav


class ProfitImportRequest(BaseModel):
    profit_data: List[ProfitImport]
    import_mode: str = "accumulate"  # overwrite/accumulate
    import_date: Optional[str] = None


@router.post("/groups/{group_id}/transactions")
async def record_transaction(group_id: int, data: TransactionCreate):
    """
    记录交易（买入或卖出）

    买入公式：
    - 新成本 = (原数量 × 原成本 + 买入投入金额) / (原数量 + 买入数量)
    - 新持仓数量 = 原数量 + 买入数量

    卖出公式：
    - 新成本 = (原数量 × 原成本 - 卖出获得金额) / (原数量 - 卖出数量)
    - 新持仓数量 = 原数量 - 卖出数量
    - 卖出所得计入组合现金
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from portfolio_manager import record_buy_transaction, record_sell_transaction

        if data.transaction_type.upper() == 'BUY':
            result = record_buy_transaction(
                portfolio_id=group_id,
                fund_code=data.fund_code,
                shares=data.shares,
                amount=data.amount,
                transaction_date=data.transaction_date,
                nav=data.nav,
                fee=data.fee,
                notes=data.notes
            )
        elif data.transaction_type.upper() == 'SELL':
            result = record_sell_transaction(
                portfolio_id=group_id,
                fund_code=data.fund_code,
                shares=data.shares,
                amount=data.amount,
                transaction_date=data.transaction_date,
                nav=data.nav,
                fee=data.fee,
                notes=data.notes
            )
        else:
            return {"success": False, "message": f"不支持的交易类型: {data.transaction_type}"}

        if result.get('success'):
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": result.get('error', '交易记录失败')}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


# ==================== 波段捡回API ====================

class BuyBackTransactionRequest(BaseModel):
    target_sell_transaction_id: int
    shares: float
    amount: float
    nav: Optional[float] = None
    transaction_date: Optional[str] = None
    fee: float = 0
    notes: Optional[str] = None


@router.post("/groups/{group_id}/funds/{fund_code}/buy-back")
async def execute_buy_back_transaction(
    group_id: int,
    fund_code: str,
    data: BuyBackTransactionRequest
):
    """
    执行波段捡回交易

    功能：
    1. 记录买入交易
    2. 标记对应的卖出记录为已回收 (is_recovered = 1)
    3. 扣除组合现金

    前置条件：
    - 目标卖出记录必须存在且未回收
    - 捡回份额必须与卖出份额一致
    - 组合现金必须充足
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import execute_buy_back_transaction as _execute_buy_back

        result = _execute_buy_back(
            portfolio_id=group_id,
            fund_code=fund_code,
            target_sell_transaction_id=data.target_sell_transaction_id,
            shares=data.shares,
            amount=data.amount,
            nav=data.nav,
            transaction_date=data.transaction_date,
            fee=data.fee,
            notes=data.notes
        )

        if result.get('success'):
            return {
                "success": True,
                "message": f"波段捡回成功：买入 {result['shares']:.2f} 份 {result['fund_name']}，花费 {result['amount']:.2f} 元",
                "data": result
            }
        else:
            return {"success": False, "message": result.get('error', '捡回失败')}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/groups/{group_id}/transactions")
async def get_transactions(
    group_id: int,
    fund_code: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取组合交易记录"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from portfolio_manager import get_portfolio_transactions

        transactions = get_portfolio_transactions(
            portfolio_id=group_id,
            fund_code=fund_code,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )

        return {"success": True, "data": transactions}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/groups/{group_id}/profit-import")
async def import_profit_data(group_id: int, data: ProfitImportRequest):
    """
    导入盈亏数据

    import_mode:
    - overwrite: 覆盖模式，替换现有数据
    - accumulate: 累加模式，与现有数据累加（默认）
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from portfolio_manager import import_profit_data

        # 转换数据格式
        profit_data = []
        for item in data.profit_data:
            profit_data.append({
                'fund_code': item.fund_code,
                'fund_name': item.fund_name,
                'profit_loss': item.profit_loss
                # current_value 由后端根据 shares × latest_nav 自动计算
            })

        result = import_profit_data(
            portfolio_id=group_id,
            profit_data=profit_data,
            import_date=data.import_date,
            import_mode=data.import_mode,
            source_type='manual'
        )

        if result.get('success'):
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": result.get('error', '导入失败')}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/groups/{group_id}/cash")
async def get_cash(group_id: int):
    """获取组合现金余额"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from portfolio_manager import get_portfolio_cash

        result = get_portfolio_cash(group_id)

        if result.get('success'):
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": result.get('error', '获取失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/groups/{group_id}/cash")
async def update_cash(group_id: int, cash: float):
    """更新组合现金余额"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from portfolio_manager import update_portfolio_cash

        result = update_portfolio_cash(group_id, cash)

        if result.get('success'):
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": result.get('error', '更新失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 投资建议API ====================

@router.get("/investment-modes")
async def get_investment_modes():
    """
    获取支持的定投模式列表
    目前支持：市值定投法
    """
    return {
        "success": True,
        "data": [
            {
                "id": "value_averaging",
                "name": "市值定投法",
                "name_en": "Value Averaging Strategy",
                "description": "根据目标市值增长额计算每期投入金额，涨时少买、跌时多买",
                "icon": "trending_up",
                "enabled": True
            },
            {
                "id": "fixed_amount",
                "name": "定额定投法",
                "name_en": "Fixed Amount Strategy",
                "description": "每期投入固定金额，简单易执行（即将上线）",
                "icon": "wallet",
                "enabled": False
            },
            {
                "id": "dynamic_balance",
                "name": "动态平衡法",
                "name_en": "Dynamic Rebalancing",
                "description": "根据资产配置比例动态调整持仓（即将上线）",
                "icon": "scale",
                "enabled": False
            }
        ]
    }


@router.post("/groups/{group_id}/investment-advice")
async def get_investment_advice(
    group_id: int,
    mode: str = Query("value_averaging", description="定投模式: value_averaging"),
    simulate: bool = Query(True, description="是否模拟多期"),
    base_days: int = Query(30, description="基准日期回溯天数，默认30天")
):
    """
    获取组合的投资建议（使用修正版市值定投算法）
    
    Args:
        group_id: 组合ID
        mode: 定投模式，目前仅支持 value_averaging（市值定投法）
        simulate: 是否模拟12期定投过程
        base_days: 基准日期回溯天数，默认30天前
    
    Returns:
        投资建议数据，包含每只基金的定投方案
    """
    from datetime import datetime, timedelta
    
    print(f"[投资建议] 收到请求: group_id={group_id}, mode={mode}, simulate={simulate}, base_days={base_days}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 获取组合信息
            cursor.execute("SELECT name FROM portfolio WHERE id = ?", (group_id,))
            portfolio_row = cursor.fetchone()
            if not portfolio_row:
                print(f"[投资建议] 组合不存在: {group_id}")
                return {"success": False, "message": "组合不存在"}
            
            portfolio_name = portfolio_row["name"]
            print(f"[投资建议] 组合名称: {portfolio_name}")
            
            # 计算基准日期和目标日期
            target_date = datetime.now().strftime('%Y-%m-%d')
            base_date = (datetime.now() - timedelta(days=base_days)).strftime('%Y-%m-%d')
            print(f"[投资建议] 基准日期: {base_date}, 目标日期: {target_date}")
            
            # 获取组合内所有基金及持仓
            cursor.execute("""
                SELECT 
                    pf.fund_code,
                    pf.fund_name,
                    pf.shares as current_shares,
                    fn.unit_nav as latest_nav
                FROM portfolio_fund pf
                LEFT JOIN (
                    SELECT fund_code, unit_nav
                    FROM fund_nav
                    WHERE (fund_code, nav_date) IN (
                        SELECT fund_code, MAX(nav_date)
                        FROM fund_nav
                        GROUP BY fund_code
                    )
                ) fn ON pf.fund_code = fn.fund_code
                WHERE pf.portfolio_id = ?
            """, (group_id,))
            
            rows = cursor.fetchall()
            print(f"[投资建议] 查询到 {len(rows)} 只基金")
            
            if not rows:
                return {
                    "success": True,
                    "data": {
                        "portfolio_id": group_id,
                        "portfolio_name": portfolio_name,
                        "mode": mode,
                        "base_date": base_date,
                        "target_date": target_date,
                        "funds": [],
                        "summary": {
                            "total_funds": 0,
                            "total_holding_value": 0,
                            "total_suggested_invest": 0
                        }
                    }
                }
            
            # 根据模式计算投资建议
            funds_advice = []
            total_holding_value = 0
            total_suggested_invest = 0
            
            if mode == "value_averaging":
                print(f"[投资建议] 开始使用市值定投法(v2)计算...")
                
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
                from value_averaging import calculate_value_averaging_v2, get_shares_at_date, get_nav_at_date
                
                # 市值定投法
                for row in rows:
                    fund_code = row["fund_code"]
                    fund_name = row["fund_name"]
                    current_shares = row["current_shares"] or 0
                    latest_nav = row["latest_nav"] or 0
                    current_holding = current_shares * latest_nav
                    
                    total_holding_value += current_holding
                    
                    print(f"[投资建议] 计算基金 {fund_code}, 当前持仓={current_holding}")
                    
                    try:
                        # 查询基准日期的持仓份额和净值
                        shares_at_base = get_shares_at_date(fund_code, group_id, base_date)
                        nav_at_base = get_nav_at_date(fund_code, base_date)
                        
                        print(f"[投资建议] 基金 {fund_code}: 基准份额={shares_at_base}, 基准净值={nav_at_base}")
                        
                        # 如果基准日期没有持仓记录，使用当前持仓作为基准
                        if shares_at_base == 0:
                            shares_at_base = current_shares
                            nav_at_base = latest_nav
                            print(f"[投资建议] 基金 {fund_code}: 无历史记录，使用当前持仓作为基准")
                        
                        # 如果基准日期没有净值，使用当前净值
                        if nav_at_base == 0:
                            nav_at_base = latest_nav
                        
                        # 调用新版市值定投算法
                        result = calculate_value_averaging_v2(
                            fund_code=fund_code,
                            shares_at_base=shares_at_base,
                            nav_at_base=nav_at_base,
                            base_date=base_date,
                            current_shares=current_shares,
                            current_nav=latest_nav,
                            target_date=target_date,
                            avg_monthly_return=None  # 自动计算
                        )
                        
                        print(f"[投资建议] 基金 {fund_code} 计算完成: 建议{result['invest_action']} {abs(result['invest_amount']):.2f}")
                        
                        suggested_invest = result["invest_amount"]
                        total_suggested_invest += suggested_invest
                        
                        funds_advice.append({
                            "fund_code": fund_code,
                            "fund_name": fund_name,
                            "base_date": base_date,
                            "target_date": target_date,
                            "days_diff": result.get("days_diff", base_days),
                            "shares_at_base": result.get("shares_at_base", 0),
                            "nav_at_base": result.get("nav_at_base", 0),
                            "base_value": result.get("base_value", 0),
                            "current_shares": current_shares,
                            "latest_nav": latest_nav,
                            "actual_value": result.get("actual_value", 0),
                            "avg_monthly_return": result.get("avg_monthly_return", 0),
                            "target_growth": result.get("target_growth", 0),
                            "target_value": result.get("target_value", 0),
                            "suggested_invest": suggested_invest,
                            "invest_action": result.get("invest_action", "未知"),
                            "original_holding_value": result.get("original_holding_value", 0),
                            "original_holding_profit": result.get("original_holding_profit", 0),
                            "market_phase": result.get("market_phase", "未知"),
                            "algorithm_details": result.get("algorithm_details", [])
                        })
                    except Exception as e:
                        print(f"[投资建议] 基金 {fund_code} 计算失败: {e}")
                        import traceback
                        traceback.print_exc()
                        funds_advice.append({
                            "fund_code": fund_code,
                            "fund_name": fund_name,
                            "current_shares": current_shares,
                            "latest_nav": latest_nav,
                            "error": str(e)
                        })
            else:
                return {"success": False, "message": f"不支持的定投模式: {mode}"}
            
            return {
                "success": True,
                "data": {
                    "portfolio_id": group_id,
                    "portfolio_name": portfolio_name,
                    "mode": mode,
                    "mode_name": "市值定投法",
                    "base_date": base_date,
                    "target_date": target_date,
                    "funds": funds_advice,
                    "summary": {
                        "total_funds": len(funds_advice),
                        "total_holding_value": total_holding_value,
                        "total_suggested_invest": total_suggested_invest,
                        "simulate": simulate
                    }
                }
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.post("/groups")
async def create_group(data: GroupCreate):
    """创建组合"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio (name, description)
                VALUES (?, ?)
            """, (data.name, data.description))
            conn.commit()
            group_id = cursor.lastrowid
            return {
                "success": True, 
                "data": {
                    "id": group_id,
                    "name": data.name,
                    "description": data.description
                }
            }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/groups/{group_id}")
async def get_group(group_id: int):
    """获取组合详情"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, create_time, update_time
                FROM portfolio WHERE id = ?
            """, (group_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="组合不存在")
            return {"success": True, "data": dict(row)}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/groups/{group_id}")
async def update_group(group_id: int, data: GroupUpdate):
    """更新组合"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            if data.name is not None:
                updates.append("name = ?")
                params.append(data.name)
            if data.description is not None:
                updates.append("description = ?")
                params.append(data.description)
            if updates:
                updates.append("update_time = datetime('now')")
                params.append(group_id)
                sql = f"UPDATE portfolio SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                conn.commit()
            return {"success": True, "message": "更新成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.delete("/groups/{group_id}")
async def delete_group(group_id: int):
    """删除组合"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portfolio WHERE id = ?", (group_id,))
            conn.commit()
            return {"success": True, "message": "删除成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/groups/{group_id}/funds")
async def get_group_funds(
    group_id: int,
    force_refresh: bool = Query(False, description="强制刷新数据"),
    include_metrics: bool = Query(True, description="包含风险收益指标")
):
    """
    获取组合中的基金列表

    使用fundData skill的聚合查询接口，自动根据数据新鲜度决定从数据库读取还是从AKShare获取最新数据
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)
        
        # 清除可能冲突的模块缓存，让Python从skills目录重新加载
        modules_to_clear = ['database', 'smart_fund_data', 'fund_data_skill', 'portfolio_manager', 
                           'risk_metrics_calculator', 'value_averaging', 'syncers', 'queries']
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
        
        from smart_fund_data import get_portfolio_funds_full

        result = get_portfolio_funds_full(
            portfolio_id=group_id,
            force_update=force_refresh
        )

        if 'error' in result:
            return {"success": False, "message": result['error']}

        # 补充计算市值和收益率，并转换字段名以兼容前端
        funds = []
        for fund in result['funds']:
            fund_code = fund['fund_code']
            fund_data = {
                'id': fund.get('id'),
                'portfolio_id': group_id,
                'fund_code': fund_code,
                'fund_name': fund['fund_name'],
                'fund_type': fund.get('fund_type'),
                'company_name': fund.get('company_name'),
                'shares': fund.get('shares'),
                'buy_date': fund.get('buy_date'),
                'buy_nav': fund.get('buy_nav'),
                'latest_nav': fund.get('unit_nav'),
                'nav_date': fund.get('nav_date'),
                'daily_return': fund.get('daily_return'),
                'notes': fund.get('notes'),
            }

            # 补充风险收益指标
            if include_metrics:
                fund_data['return_1m'] = fund.get('return_1m')
                fund_data['return_6m'] = fund.get('return_6m')
                fund_data['return_1y'] = fund.get('return_1y')
                fund_data['max_drawdown_1y'] = fund.get('max_drawdown_1y')
                fund_data['sharpe_ratio_1y'] = fund.get('sharpe_ratio_1y')
                fund_data['annual_volatility_1y'] = fund.get('annual_volatility_1y')
                fund_data['rank_in_category'] = fund.get('rank_in_category')
                fund_data['rank_category'] = fund.get('rank_category')
                fund_data['metrics_update_time'] = fund.get('metrics_update_time')

            # 计算市值、成本和盈亏（实时计算）
            print(f"[API] 基金 {fund_code}: shares={fund_data.get('shares')}, buy_nav={fund_data.get('buy_nav')}, latest_nav={fund_data.get('latest_nav')}")
            if fund_data.get('shares') and fund_data.get('latest_nav'):
                fund_data['market_value'] = fund_data['shares'] * fund_data['latest_nav']
                if fund_data.get('buy_nav'):
                    fund_data['cost'] = fund_data['shares'] * fund_data['buy_nav']
                    fund_data['profit_loss'] = fund_data['market_value'] - fund_data['cost']
                    fund_data['profit_rate'] = (fund_data['latest_nav'] - fund_data['buy_nav']) / fund_data['buy_nav'] * 100
                    print(f"[API] 基金 {fund_code}: 计算盈亏 profit_loss={fund_data['profit_loss']}")
                else:
                    fund_data['cost'] = None
                    fund_data['profit_loss'] = None
                    fund_data['profit_rate'] = 0
                    print(f"[API] 基金 {fund_code}: buy_nav为空, 不计算盈亏")
            else:
                fund_data['market_value'] = None
                fund_data['cost'] = None
                fund_data['profit_loss'] = None
                fund_data['profit_rate'] = 0
                print(f"[API] 基金 {fund_code}: shares或latest_nav为空, 不计算市值")

            # 添加可用现金（实时计算）
            available_cash = fund.get('available_cash')
            if available_cash is not None:
                fund_data['available_cash'] = available_cash
                fund_data['total_buy_amount'] = fund.get('total_buy_amount')
                fund_data['total_sell_amount'] = fund.get('total_sell_amount')
                print(f"[API] 基金 {fund_code}: 可用现金 available_cash={available_cash}")

            funds.append(fund_data)

        return {
            "success": True,
            "data": funds,
            "freshness_summary": result.get('freshness_summary', {})
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.post("/groups/{group_id}/funds")
async def add_fund_to_group(group_id: int, data: AddFundToGroup):
    """添加基金到组合"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 检查基金是否存在
            cursor.execute("SELECT fund_name FROM fund_info WHERE fund_code = ?", (data.fund_code,))
            fund_row = cursor.fetchone()
            if not fund_row:
                return {"success": False, "message": "基金不存在"}
            
            fund_name = data.fund_name or fund_row["fund_name"]
            
            cursor.execute("""
                INSERT OR REPLACE INTO portfolio_fund 
                (portfolio_id, fund_code, fund_name, shares, buy_date, buy_nav, amount, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (group_id, data.fund_code, fund_name, data.shares, 
                  data.buy_date, data.buy_nav, data.amount))
            conn.commit()
            return {"success": True, "message": "添加成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.delete("/groups/{group_id}/funds/{fund_code}")
async def remove_fund_from_group(group_id: int, fund_code: str):
    """从组合移除基金"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM portfolio_fund 
                WHERE portfolio_id = ? AND fund_code = ?
            """, (group_id, fund_code))
            conn.commit()
            return {"success": True, "message": "移除成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/funds/{fund_code}/groups")
async def get_fund_groups(fund_code: str):
    """获取基金所属的组合列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description
                FROM portfolio p
                JOIN portfolio_fund pf ON p.id = pf.portfolio_id
                WHERE pf.fund_code = ?
            """, (fund_code,))
            rows = cursor.fetchall()
            groups = [dict(row) for row in rows]
            return {"success": True, "data": groups}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 持仓历史API ====================

@router.get("/groups/{group_id}/history")
async def get_group_history(group_id: int, limit: int = Query(100)):
    """获取组合持仓历史"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.*, fi.fund_name
                FROM holding_history h
                JOIN fund_info fi ON h.fund_code = fi.fund_code
                WHERE h.portfolio_id = ?
                ORDER BY h.record_date DESC
                LIMIT ?
            """, (group_id, limit))
            rows = cursor.fetchall()
            history = [dict(row) for row in rows]
            return {"success": True, "data": history}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 组合汇总API ====================

@router.get("/summary")
async def get_portfolio_summary(group_id: Optional[int] = Query(None)):
    """获取投资组合汇总 - 优先使用数据库中的profit_loss字段"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = "WHERE pf.portfolio_id = ?" if group_id else ""
            params = [group_id] if group_id else []
            
            # 获取每只基金的持仓详情，包括profit_loss字段
            cursor.execute(f"""
                SELECT 
                    pf.fund_code,
                    pf.shares,
                    pf.buy_nav,
                    pf.profit_loss,
                    fn.unit_nav as latest_nav
                FROM portfolio_fund pf
                LEFT JOIN (
                    SELECT fund_code, unit_nav
                    FROM fund_nav
                    WHERE (fund_code, nav_date) IN (
                        SELECT fund_code, MAX(nav_date)
                        FROM fund_nav
                        GROUP BY fund_code
                    )
                ) fn ON pf.fund_code = fn.fund_code
                {where_clause}
            """, params)
            
            rows = cursor.fetchall()
            
            total_cost = 0
            total_market_value = 0
            total_profit = 0
            position_count = len(rows)
            
            for row in rows:
                shares = row["shares"] or 0
                buy_nav = row["buy_nav"] or 0
                latest_nav = row["latest_nav"] or 0
                profit_loss = row["profit_loss"]
                
                # 计算市值
                market_value = shares * latest_nav
                total_market_value += market_value
                
                # 计算成本：使用 shares * buy_nav
                if shares > 0 and buy_nav > 0:
                    cost = shares * buy_nav
                else:
                    cost = 0
                
                total_cost += cost
                
                # 计算盈亏：优先使用数据库中的profit_loss，否则计算
                if profit_loss is not None:
                    total_profit += profit_loss
                else:
                    total_profit += (market_value - cost)
            
            total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
            
            summary = {
                "position_count": position_count,
                "total_cost": total_cost,
                "total_market_value": total_market_value,
                "total_profit": total_profit,
                "total_profit_rate": total_profit_rate
            }
            
            return {"success": True, "data": summary}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 刷新数据API ====================

@router.post("/groups/{group_id}/refresh")
async def refresh_group_data(group_id: int):
    """
    刷新组合数据 - 从fundData获取最新净值
    注意：fundData skill会自动维护数据新鲜度
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 获取组合内所有基金
            cursor.execute("""
                SELECT fund_code FROM portfolio_fund WHERE portfolio_id = ?
            """, (group_id,))
            fund_codes = [row["fund_code"] for row in cursor.fetchall()]
            
            if not fund_codes:
                return {
                    "success": True,
                    "message": "组合内没有基金",
                    "data": {"updated": 0, "total": 0}
                }
            
            # 查询最新净值（fundData已维护）
            updated_count = 0
            for fund_code in fund_codes:
                cursor.execute("""
                    SELECT unit_nav, nav_date
                    FROM fund_nav
                    WHERE fund_code = ?
                    ORDER BY nav_date DESC
                    LIMIT 1
                """, (fund_code,))
                row = cursor.fetchone()
                if row:
                    updated_count += 1
            
            return {
                "success": True,
                "message": f"刷新完成，已更新 {updated_count}/{len(fund_codes)} 只基金",
                "data": {
                    "updated": updated_count,
                    "total": len(fund_codes)
                }
            }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 止盈参数模板API ====================

class TakeProfitTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    first_threshold: float = 0.20
    first_sell_ratio: float = 0.30
    step_size: float = 0.05
    follow_up_sell_ratio: float = 0.20
    enable_cost_control: bool = True
    target_diluted_cost: float = 0.0
    enable_buy_back: bool = False
    buy_back_threshold: float = 0.20


class TakeProfitTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    first_threshold: Optional[float] = None
    first_sell_ratio: Optional[float] = None
    step_size: Optional[float] = None
    follow_up_sell_ratio: Optional[float] = None
    enable_cost_control: Optional[bool] = None
    target_diluted_cost: Optional[float] = None
    enable_buy_back: Optional[bool] = None
    buy_back_threshold: Optional[float] = None


class FundTakeProfitConfigUpdate(BaseModel):
    template_id: Optional[int] = None
    use_custom: Optional[bool] = False
    custom_first_threshold: Optional[float] = None
    custom_first_sell_ratio: Optional[float] = None
    custom_step_size: Optional[float] = None
    custom_follow_up_sell_ratio: Optional[float] = None
    custom_enable_cost_control: Optional[bool] = None
    custom_target_diluted_cost: Optional[float] = None
    custom_enable_buy_back: Optional[bool] = None
    custom_buy_back_threshold: Optional[float] = None


@router.get("/take-profit-templates")
async def list_take_profit_templates():
    """获取所有止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import list_take_profit_templates as _list_templates

        templates = _list_templates()
        return {"success": True, "data": templates}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/take-profit-templates/{template_id}")
async def get_take_profit_template(template_id: int):
    """获取单个止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import get_take_profit_template as _get_template

        template = _get_template(template_id)
        if template:
            return {"success": True, "data": template}
        else:
            return {"success": False, "message": "模板不存在"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/take-profit-templates")
async def create_take_profit_template(data: TakeProfitTemplateCreate):
    """创建止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import create_take_profit_template as _create_template

        result = _create_template(
            name=data.name,
            description=data.description,
            first_threshold=data.first_threshold,
            first_sell_ratio=data.first_sell_ratio,
            step_size=data.step_size,
            follow_up_sell_ratio=data.follow_up_sell_ratio,
            enable_cost_control=data.enable_cost_control,
            target_diluted_cost=data.target_diluted_cost,
            enable_buy_back=data.enable_buy_back,
            buy_back_threshold=data.buy_back_threshold
        )

        if result.get('success'):
            return {"success": True, "data": {"template_id": result.get('template_id')}}
        else:
            return {"success": False, "message": result.get('message', '创建失败')}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.put("/take-profit-templates/{template_id}")
async def update_take_profit_template(template_id: int, data: TakeProfitTemplateUpdate):
    """更新止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import update_take_profit_template as _update_template

        update_data = data.dict(exclude_unset=True)
        result = _update_template(template_id, **update_data)

        if result.get('success'):
            return {"success": True, "message": result.get('message', '更新成功')}
        else:
            return {"success": False, "message": result.get('message', '更新失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.delete("/take-profit-templates/{template_id}")
async def delete_take_profit_template(template_id: int):
    """删除止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import delete_take_profit_template as _delete_template

        result = _delete_template(template_id)

        if result.get('success'):
            return {"success": True, "message": result.get('message', '删除成功')}
        else:
            return {"success": False, "message": result.get('message', '删除失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/take-profit-templates/{template_id}/set-default")
async def set_default_take_profit_template(template_id: int):
    """设置默认止盈参数模板"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import set_default_take_profit_template as _set_default

        result = _set_default(template_id)

        if result.get('success'):
            return {"success": True, "message": result.get('message', '设置成功')}
        else:
            return {"success": False, "message": result.get('message', '设置失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 基金止盈配置API ====================

@router.get("/groups/{group_id}/funds/{fund_code}/take-profit-config")
async def get_fund_take_profit_config(group_id: int, fund_code: str):
    """获取基金的止盈配置"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import get_fund_take_profit_config as _get_config

        config = _get_config(group_id, fund_code)
        return {"success": True, "data": config}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.put("/groups/{group_id}/funds/{fund_code}/take-profit-config")
async def set_fund_take_profit_config(group_id: int, fund_code: str, data: FundTakeProfitConfigUpdate):
    """设置基金的止盈配置"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import (
            set_fund_take_profit_template as _set_template,
            set_fund_take_profit_custom_params as _set_custom,
            reset_fund_take_profit_config as _reset_config
        )

        if data.use_custom:
            custom_params = {}
            if data.custom_first_threshold is not None:
                custom_params['first_threshold'] = data.custom_first_threshold
            if data.custom_first_sell_ratio is not None:
                custom_params['first_sell_ratio'] = data.custom_first_sell_ratio
            if data.custom_step_size is not None:
                custom_params['step_size'] = data.custom_step_size
            if data.custom_follow_up_sell_ratio is not None:
                custom_params['follow_up_sell_ratio'] = data.custom_follow_up_sell_ratio
            if data.custom_enable_cost_control is not None:
                custom_params['enable_cost_control'] = data.custom_enable_cost_control
            if data.custom_target_diluted_cost is not None:
                custom_params['target_diluted_cost'] = data.custom_target_diluted_cost
            if data.custom_enable_buy_back is not None:
                custom_params['enable_buy_back'] = data.custom_enable_buy_back
            if data.custom_buy_back_threshold is not None:
                custom_params['buy_back_threshold'] = data.custom_buy_back_threshold

            result = _set_custom(group_id, fund_code, **custom_params)
        elif data.template_id is not None:
            result = _set_template(group_id, fund_code, data.template_id)
        else:
            result = _reset_config(group_id, fund_code)

        if result.get('success'):
            return {"success": True, "message": result.get('message', '设置成功')}
        else:
            return {"success": False, "message": result.get('message', '设置失败')}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.delete("/groups/{group_id}/funds/{fund_code}/take-profit-config")
async def reset_fund_take_profit_config(group_id: int, fund_code: str):
    """重置基金止盈配置为默认"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import reset_fund_take_profit_config as _reset_config

        result = _reset_config(group_id, fund_code)

        if result.get('success'):
            return {"success": True, "message": result.get('message', '重置成功')}
        else:
            return {"success": False, "message": result.get('message', '重置失败')}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/groups/{group_id}/take-profit-configs")
async def get_portfolio_take_profit_configs(group_id: int):
    """获取组合内所有基金的止盈配置"""
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import get_portfolio_take_profit_configs as _get_configs

        configs = _get_configs(group_id)
        return {"success": True, "data": configs}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ==================== 止盈建议API ====================

@router.get("/take-profit-modes")
async def get_take_profit_modes():
    """获取支持的止盈模式列表"""
    return {
        "success": True,
        "data": [
            {
                "id": "ladder",
                "name": "阶梯止盈法",
                "name_en": "Ladder Take Profit",
                "description": "首次盈利达到阈值卖出部分，后续每涨一定比例再卖出",
                "icon": "trending_down",
                "enabled": True
            }
        ]
    }


@router.get("/groups/{group_id}/take-profit-advice")
async def get_take_profit_advice(group_id: int):
    """
    获取组合的止盈建议（支持波段捡回）

    使用各基金配置的参数计算止盈建议，包括：
    - 初次止盈：收益率 >= 首次止盈阈值 -> 卖出
    - 后续止盈：较上次卖出净值涨幅 >= 阶梯步长 -> 卖出
    - 波段捡回：净值低于最近一次卖出价格达到捡回阈值 -> 买入（高抛低吸）
    """
    try:
        import sys
        import os
        skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))
        if skills_path not in sys.path:
            sys.path.insert(0, skills_path)

        from smart_fund_data import get_take_profit_advice as _get_advice

        result = _get_advice(group_id)

        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}
