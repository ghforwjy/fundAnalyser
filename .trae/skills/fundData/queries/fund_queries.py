"""
基金数据查询模块
提供各种基金数据查询功能
"""
from typing import List, Dict, Any, Optional
from funddb import get_db_connection, get_table_stats


def search_funds(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    搜索基金
    支持按基金代码、名称、拼音搜索
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
    
    Returns:
        基金列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 支持代码、名称、拼音搜索
        search_pattern = f"%{keyword}%"
        cursor.execute('''
            SELECT fund_code, fund_name, fund_type, company_name, pinyin_abbr
            FROM fund_info
            WHERE fund_code LIKE ? 
               OR fund_name LIKE ? 
               OR pinyin_abbr LIKE ?
               OR pinyin_full LIKE ?
            ORDER BY 
                CASE 
                    WHEN fund_code = ? THEN 1
                    WHEN fund_code LIKE ? THEN 2
                    WHEN fund_name LIKE ? THEN 3
                    ELSE 4
                END
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, search_pattern,
              keyword, f"{keyword}%", f"%{keyword}%", limit))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'fund_code': row['fund_code'],
                'fund_name': row['fund_name'],
                'fund_type': row['fund_type'],
                'company_name': row['company_name'],
                'pinyin_abbr': row['pinyin_abbr']
            })
        
        return results


def get_fund_detail(fund_code: str) -> Optional[Dict[str, Any]]:
    """
    获取基金详细信息
    
    Args:
        fund_code: 基金代码
    
    Returns:
        基金详细信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fund_info WHERE fund_code = ?
        ''', (fund_code,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return dict(row)


def query_fund_nav(fund_code: str, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    查询基金净值历史
    
    Args:
        fund_code: 基金代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        limit: 返回记录数限制
    
    Returns:
        净值历史列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT nav_date, unit_nav, accum_nav, daily_return
            FROM fund_nav
            WHERE fund_code = ?
        '''
        params = [fund_code]
        
        if start_date:
            query += ' AND nav_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND nav_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY nav_date DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'nav_date': row['nav_date'],
                'unit_nav': row['unit_nav'],
                'accum_nav': row['accum_nav'],
                'daily_return': row['daily_return']
            })
        
        return results


def query_fund_rating(fund_code: str = None) -> List[Dict[str, Any]]:
    """
    查询基金评级
    
    Args:
        fund_code: 基金代码，不传则返回所有评级数据
    
    Returns:
        评级数据列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if fund_code:
            cursor.execute('''
                SELECT r.*, i.fund_name, i.fund_type
                FROM fund_rating r
                JOIN fund_info i ON r.fund_code = i.fund_code
                WHERE r.fund_code = ?
            ''', (fund_code,))
        else:
            cursor.execute('''
                SELECT r.*, i.fund_name, i.fund_type
                FROM fund_rating r
                JOIN fund_info i ON r.fund_code = i.fund_code
                LIMIT 100
            ''')
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'fund_code': row['fund_code'],
                'fund_name': row['fund_name'],
                'fund_type': row['fund_type'],
                'manager_name': row['manager_name'],
                'company_name': row['company_name'],
                'rating_5star_count': row['rating_5star_count'],
                'rating_sh': row['rating_sh'],
                'rating_zs': row['rating_zs'],
                'rating_ja': row['rating_ja'],
                'rating_morningstar': row['rating_morningstar']
            })
        
        return results


def query_fund_manager(fund_code: str = None, manager_name: str = None) -> List[Dict[str, Any]]:
    """
    查询基金经理信息
    
    Args:
        fund_code: 基金代码
        manager_name: 基金经理姓名
    
    Returns:
        基金经理信息列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT m.*, i.fund_name
            FROM fund_manager m
            JOIN fund_info i ON m.fund_code = i.fund_code
            WHERE 1=1
        '''
        params = []
        
        if fund_code:
            query += ' AND m.fund_code = ?'
            params.append(fund_code)
        
        if manager_name:
            query += ' AND m.manager_name LIKE ?'
            params.append(f"%{manager_name}%")
        
        query += ' ORDER BY m.tenure_days DESC LIMIT 100'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'manager_name': row['manager_name'],
                'company_name': row['company_name'],
                'fund_code': row['fund_code'],
                'fund_name': row['fund_name'],
                'tenure_days': row['tenure_days'],
                'total_scale': row['total_scale'],
                'best_return': row['best_return']
            })
        
        return results


def query_fund_holdings(fund_code: str, year: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    查询基金持仓数据
    
    Args:
        fund_code: 基金代码
        year: 年份
    
    Returns:
        包含股票持仓、债券持仓、行业配置的字典
    """
    from datetime import datetime
    
    if not year:
        year = str(datetime.now().year)
    
    results = {
        'stock_holdings': [],
        'bond_holdings': [],
        'industry_allocation': []
    }
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 股票持仓
        cursor.execute('''
            SELECT * FROM fund_stock_holding
            WHERE fund_code = ? AND quarter LIKE ?
            ORDER BY report_date DESC, hold_ratio DESC
        ''', (fund_code, f"%{year}%"))
        
        for row in cursor.fetchall():
            results['stock_holdings'].append({
                'stock_code': row['stock_code'],
                'stock_name': row['stock_name'],
                'hold_ratio': row['hold_ratio'],
                'hold_value': row['hold_value'],
                'quarter': row['quarter']
            })
        
        # 债券持仓
        cursor.execute('''
            SELECT * FROM fund_bond_holding
            WHERE fund_code = ? AND quarter LIKE ?
            ORDER BY report_date DESC, hold_ratio DESC
        ''', (fund_code, f"%{year}%"))
        
        for row in cursor.fetchall():
            results['bond_holdings'].append({
                'bond_code': row['bond_code'],
                'bond_name': row['bond_name'],
                'hold_ratio': row['hold_ratio'],
                'hold_value': row['hold_value'],
                'quarter': row['quarter']
            })
        
        # 行业配置
        cursor.execute('''
            SELECT * FROM fund_industry_allocation
            WHERE fund_code = ? AND quarter LIKE ?
            ORDER BY report_date DESC, allocation_ratio DESC
        ''', (fund_code, f"%{year}%"))
        
        for row in cursor.fetchall():
            results['industry_allocation'].append({
                'industry_name': row['industry_name'],
                'allocation_ratio': row['allocation_ratio'],
                'market_value': row['market_value'],
                'quarter': row['quarter']
            })
        
        return results


def query_fund_risk(fund_code: str) -> List[Dict[str, Any]]:
    """
    查询基金风险指标
    
    Args:
        fund_code: 基金代码
    
    Returns:
        风险指标列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fund_risk_metrics
            WHERE fund_code = ?
            ORDER BY period
        ''', (fund_code,))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'period': row['period'],
                'sharpe_ratio': row['sharpe_ratio'],
                'max_drawdown': row['max_drawdown'],
                'annual_volatility': row['annual_volatility'],
                'risk_return_ratio': row['risk_return_ratio'],
                'risk_resistance': row['risk_resistance']
            })
        
        return results


def query_fund_performance(fund_code: str) -> List[Dict[str, Any]]:
    """
    查询基金业绩表现
    
    Args:
        fund_code: 基金代码
    
    Returns:
        业绩表现列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fund_performance
            WHERE fund_code = ?
            ORDER BY performance_type, period
        ''', (fund_code,))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'performance_type': row['performance_type'],
                'period': row['period'],
                'period_return': row['period_return'],
                'max_drawdown': row['max_drawdown'],
                'rank_in_category': row['rank_in_category']
            })
        
        return results


def query_sync_status() -> Dict[str, Any]:
    """
    查询数据同步状态
    
    Returns:
        各数据表的同步状态
    """
    return get_table_stats()


def get_fund_stats() -> Dict[str, Any]:
    """
    获取基金数据统计信息
    
    Returns:
        统计信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 基金总数
        cursor.execute("SELECT COUNT(*) as count FROM fund_info")
        total_funds = cursor.fetchone()['count']
        
        # 按类型统计
        cursor.execute('''
            SELECT fund_type, COUNT(*) as count 
            FROM fund_info 
            GROUP BY fund_type
            ORDER BY count DESC
        ''')
        type_distribution = {row['fund_type']: row['count'] for row in cursor.fetchall()}
        
        # 按公司统计（前10）
        cursor.execute('''
            SELECT company_name, COUNT(*) as count 
            FROM fund_info 
            WHERE company_name != ''
            GROUP BY company_name
            ORDER BY count DESC
            LIMIT 10
        ''')
        company_distribution = {row['company_name']: row['count'] for row in cursor.fetchall()}
        
        # 净值数据覆盖
        cursor.execute('''
            SELECT COUNT(DISTINCT fund_code) as count FROM fund_nav
        ''')
        nav_coverage = cursor.fetchone()['count']
        
        return {
            'total_funds': total_funds,
            'type_distribution': type_distribution,
            'top_companies': company_distribution,
            'nav_coverage': nav_coverage,
            'nav_coverage_rate': f"{nav_coverage/total_funds*100:.1f}%" if total_funds > 0 else "0%"
        }
