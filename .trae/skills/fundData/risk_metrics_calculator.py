"""
风险指标计算模块
基于净值数据计算最大回撤、年化波动率、夏普比率等风险指标
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from funddb import get_db_connection


def calc_max_drawdown(nav_series: List[float]) -> Tuple[float, int, int]:
    """
    计算最大回撤
    
    Args:
        nav_series: 净值序列（按时间升序）
    
    Returns:
        (最大回撤百分比, 最高点位置, 最低点位置)
    
    算法：
        遍历净值序列，记录历史最高点
        计算每个时点相对于历史最高点的回撤
        取最大值
    """
    if not nav_series or len(nav_series) < 2:
        return 0.0, 0, 0
    
    max_nav = nav_series[0]
    max_drawdown = 0.0
    peak_idx = 0
    trough_idx = 0
    current_peak_idx = 0
    
    for i, nav in enumerate(nav_series):
        if nav > max_nav:
            max_nav = nav
            current_peak_idx = i
        
        drawdown = (max_nav - nav) / max_nav
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            peak_idx = current_peak_idx
            trough_idx = i
    
    return max_drawdown * 100, peak_idx, trough_idx


def calc_annual_volatility(daily_returns: List[float], trading_days: int = 252) -> float:
    """
    计算年化波动率
    
    Args:
        daily_returns: 日收益率序列
        trading_days: 年交易日数，默认252
    
    Returns:
        年化波动率（百分比）
    
    算法：
        年化波动率 = 日收益率标准差 × sqrt(252)
    """
    if not daily_returns or len(daily_returns) < 2:
        return 0.0
    
    std = np.std(daily_returns, ddof=1)
    annual_vol = std * np.sqrt(trading_days)
    
    return annual_vol * 100


def calc_sharpe_ratio(annual_return: float, annual_volatility: float, risk_free_rate: float = 0.025) -> float:
    """
    计算夏普比率
    
    Args:
        annual_return: 年化收益率（百分比）
        annual_volatility: 年化波动率（百分比）
        risk_free_rate: 无风险利率，默认2.5%
    
    Returns:
        夏普比率
    
    算法：
        夏普比率 = (年化收益率 - 无风险利率) / 年化波动率
    """
    if annual_volatility <= 0:
        return 0.0
    
    return (annual_return / 100 - risk_free_rate) / (annual_volatility / 100)


def calc_period_return(nav_series: List[float]) -> float:
    """
    计算区间收益率
    
    Args:
        nav_series: 净值序列（按时间升序，第一个为期初，最后一个为期末）
    
    Returns:
        区间收益率（百分比）
    
    算法：
        区间收益率 = (期末净值 / 期初净值) - 1
    """
    if not nav_series or len(nav_series) < 2:
        return 0.0
    
    return (nav_series[-1] / nav_series[0] - 1) * 100


def calc_annual_return(nav_series: List[float], trading_days: int) -> float:
    """
    计算年化收益率
    
    Args:
        nav_series: 净值序列（按时间升序）
        trading_days: 实际交易日数
    
    Returns:
        年化收益率（百分比）
    
    算法：
        年化收益率 = (期末净值 / 期初净值)^(252/天数) - 1
    """
    if not nav_series or len(nav_series) < 2 or trading_days <= 0:
        return 0.0
    
    total_return = nav_series[-1] / nav_series[0]
    annual_return = (total_return ** (252 / trading_days)) - 1
    
    return annual_return * 100


def calc_daily_returns(nav_series: List[float]) -> List[float]:
    """
    计算日收益率序列
    
    Args:
        nav_series: 净值序列（按时间升序）
    
    Returns:
        日收益率序列
    """
    if not nav_series or len(nav_series) < 2:
        return []
    
    returns = []
    for i in range(1, len(nav_series)):
        if nav_series[i-1] > 0:
            ret = (nav_series[i] - nav_series[i-1]) / nav_series[i-1]
            returns.append(ret)
    
    return returns


def calculate_risk_metrics_from_nav(nav_data: List[Dict[str, Any]], 
                                     period: str = '近1年',
                                     risk_free_rate: float = 0.025) -> Dict[str, Any]:
    """
    从净值数据计算风险指标
    
    Args:
        nav_data: 净值数据列表，每项包含 nav_date, unit_nav
        period: 周期名称
        risk_free_rate: 无风险利率
    
    Returns:
        风险指标字典
    """
    if not nav_data or len(nav_data) < 2:
        return {
            'success': False,
            'error': '净值数据不足',
            'period': period
        }
    
    nav_series = [float(d['unit_nav']) for d in nav_data if d['unit_nav']]
    trading_days = len(nav_series)
    
    if trading_days < 2:
        return {
            'success': False,
            'error': '有效净值数据不足',
            'period': period
        }
    
    start_date = nav_data[0]['nav_date']
    end_date = nav_data[-1]['nav_date']
    
    max_drawdown, _, _ = calc_max_drawdown(nav_series)
    daily_returns = calc_daily_returns(nav_series)
    annual_volatility = calc_annual_volatility(daily_returns) if len(daily_returns) >= 20 else None
    period_return = calc_period_return(nav_series)
    annual_return = calc_annual_return(nav_series, trading_days) if trading_days >= 126 else None
    sharpe_ratio = calc_sharpe_ratio(annual_return, annual_volatility, risk_free_rate) if annual_volatility and annual_return else None
    
    return {
        'success': True,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'trading_days': trading_days,
        'period_return': round(period_return, 4) if period_return else None,
        'annual_return': round(annual_return, 4) if annual_return else None,
        'max_drawdown': round(max_drawdown, 4) if max_drawdown else None,
        'annual_volatility': round(annual_volatility, 4) if annual_volatility else None,
        'sharpe_ratio': round(sharpe_ratio, 4) if sharpe_ratio else None,
        'risk_free_rate': risk_free_rate,
        'data_source': 'calculated'
    }


def compare_with_xueqiu(calc_result: Dict[str, Any], xueqiu_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    对比自计算与雪球的风险指标
    
    Args:
        calc_result: 自计算结果
        xueqiu_data: 雪球数据
    
    Returns:
        对比结果
    """
    comparison = {
        'fund_code': calc_result.get('fund_code'),
        'period': calc_result.get('period'),
        'calc': {
            'max_drawdown': calc_result.get('max_drawdown'),
            'annual_volatility': calc_result.get('annual_volatility'),
            'sharpe_ratio': calc_result.get('sharpe_ratio')
        },
        'xueqiu': {
            'max_drawdown': xueqiu_data.get('max_drawdown'),
            'annual_volatility': xueqiu_data.get('annual_volatility'),
            'sharpe_ratio': xueqiu_data.get('sharpe_ratio')
        },
        'diff': {},
        'is_consistent': True,
        'issues': []
    }
    
    for metric in ['max_drawdown', 'annual_volatility', 'sharpe_ratio']:
        calc_val = calc_result.get(metric)
        xq_val = xueqiu_data.get(metric)
        
        if calc_val is not None and xq_val is not None:
            diff = abs(calc_val - xq_val)
            comparison['diff'][metric] = round(diff, 4)
            
            if metric == 'max_drawdown' and diff > 2:
                comparison['is_consistent'] = False
                comparison['issues'].append(f'最大回撤差异{diff:.2f}%')
            elif metric == 'annual_volatility' and diff > 3:
                comparison['is_consistent'] = False
                comparison['issues'].append(f'年化波动率差异{diff:.2f}%')
            elif metric == 'sharpe_ratio' and diff > 0.3:
                comparison['is_consistent'] = False
                comparison['issues'].append(f'夏普比率差异{diff:.2f}')
    
    return comparison


def calculate_fund_risk_metrics(fund_code: str, 
                                 period: str = '近1年',
                                 force_update: bool = False) -> Dict[str, Any]:
    """
    计算单只基金的风险指标
    
    自动获取净值数据并计算风险指标，结果存入数据库
    
    Args:
        fund_code: 基金代码
        period: 计算周期（近1年、近3年、近5年、成立以来）
        force_update: 是否强制更新
    
    Returns:
        计算结果
    """
    from funddb import get_db_connection
    from syncers import sync_group_nav
    
    period_days = {
        '近1月': 21,
        '近6月': 126,
        '近1年': 252,
        '近3年': 756,
        '近5年': 1260,
        '成立以来': None
    }
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if not force_update:
            cursor.execute('''
                SELECT * FROM fund_risk_metrics
                WHERE fund_code = ? AND period = ? AND data_source = 'calculated'
            ''', (fund_code, period))
            row = cursor.fetchone()
            
            if row and row['update_time']:
                cursor.execute('SELECT MAX(nav_date) as latest FROM fund_nav WHERE fund_code = ?', (fund_code,))
                latest_nav = cursor.fetchone()
                
                if latest_nav and latest_nav['latest']:
                    calc_end = row['calc_end_date']
                    if calc_end and calc_end >= latest_nav['latest']:
                        return {
                            'success': True,
                            'fund_code': fund_code,
                            'period': period,
                            'start_date': row['calc_start_date'],
                            'end_date': row['calc_end_date'],
                            'trading_days': row['trading_days'],
                            'period_return': row['period_return'],
                            'max_drawdown': row['max_drawdown'],
                            'annual_volatility': row['annual_volatility'],
                            'sharpe_ratio': row['sharpe_ratio'],
                            'from_cache': True,
                            'message': '使用缓存数据'
                        }
        
        cursor.execute('SELECT COUNT(*) as cnt FROM fund_nav WHERE fund_code = ?', (fund_code,))
        nav_count = cursor.fetchone()['cnt']
        
        if nav_count < 20:
            print(f"[RiskCalc] {fund_code} 净值数据不足({nav_count}条)，尝试获取...")
            sync_group_nav([fund_code])
            
            cursor.execute('SELECT COUNT(*) as cnt FROM fund_nav WHERE fund_code = ?', (fund_code,))
            nav_count = cursor.fetchone()['cnt']
            
            if nav_count < 20:
                return {
                    'success': False,
                    'fund_code': fund_code,
                    'period': period,
                    'error': f'净值数据不足({nav_count}条)'
                }
        
        days = period_days.get(period)
        if days:
            cursor.execute('''
                SELECT nav_date, unit_nav FROM fund_nav
                WHERE fund_code = ?
                ORDER BY nav_date DESC
                LIMIT ?
            ''', (fund_code, days))
            nav_data = cursor.fetchall()
            nav_data = list(reversed(nav_data))
        else:
            cursor.execute('''
                SELECT nav_date, unit_nav FROM fund_nav
                WHERE fund_code = ?
                ORDER BY nav_date ASC
            ''', (fund_code,))
            nav_data = cursor.fetchall()
        
        if not nav_data:
            return {
                'success': False,
                'fund_code': fund_code,
                'period': period,
                'error': '无净值数据'
            }
        
        result = calculate_risk_metrics_from_nav(nav_data, period)
        result['fund_code'] = fund_code
        
        if not result.get('success'):
            return result
        
        cursor.execute('''
            INSERT OR REPLACE INTO fund_risk_metrics
            (fund_code, period, max_drawdown, annual_volatility, sharpe_ratio,
             data_source, calc_start_date, calc_end_date, trading_days, period_return, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            fund_code, period,
            result.get('max_drawdown'),
            result.get('annual_volatility'),
            result.get('sharpe_ratio'),
            'calculated',
            result.get('start_date'),
            result.get('end_date'),
            result.get('trading_days'),
            result.get('period_return')
        ))
        
        conn.commit()
        
        return result


def calculate_portfolio_risk_metrics(portfolio_id: int = None,
                                      portfolio_name: str = None,
                                      force_update: bool = False) -> Dict[str, Any]:
    """
    计算组合内所有基金的风险指标
    
    Args:
        portfolio_id: 组合ID
        portfolio_name: 组合名称
        force_update: 是否强制更新
    
    Returns:
        计算报告
    """
    from portfolio_manager import list_portfolios, list_portfolio_funds
    from syncers.group_syncers import sync_single_fund_risk
    
    if not portfolio_id and not portfolio_name:
        portfolios = list_portfolios()
        if portfolios:
            portfolio_id = portfolios[0]['id']
            portfolio_name = portfolios[0]['name']
        else:
            return {'error': '没有找到任何组合'}
    
    if not portfolio_id:
        portfolios = list_portfolios()
        for p in portfolios:
            if p['name'] == portfolio_name:
                portfolio_id = p['id']
                break
    
    funds = list_portfolio_funds(portfolio_id)
    if not funds:
        return {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio_name,
            'fund_count': 0,
            'results': []
        }
    
    results = []
    success_count = 0
    skip_count = 0
    comparisons = []
    
    periods = ['近1年', '成立以来']
    
    for fund in funds:
        fund_code = fund['fund_code']
        fund_name = fund.get('fund_name', '')
        fund_result = {
            'fund_code': fund_code,
            'fund_name': fund_name,
            'periods': []
        }
        
        for period in periods:
            calc_result = calculate_fund_risk_metrics(fund_code, period, force_update)
            
            if calc_result.get('success'):
                success_count += 1
                fund_result['periods'].append({
                    'period': period,
                    'success': True,
                    'data': calc_result
                })
                
                xq_result = sync_single_fund_risk(fund_code)
                if xq_result.get('success'):
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT max_drawdown, annual_volatility, sharpe_ratio
                            FROM fund_risk_metrics
                            WHERE fund_code = ? AND period = ? AND data_source = 'xueqiu'
                        ''', (fund_code, period))
                        xq_data = cursor.fetchone()
                    
                    if xq_data:
                        comparison = compare_with_xueqiu(
                            {**calc_result, 'fund_code': fund_code},
                            dict(xq_data)
                        )
                        comparisons.append(comparison)
            else:
                skip_count += 1
                fund_result['periods'].append({
                    'period': period,
                    'success': False,
                    'error': calc_result.get('error')
                })
        
        results.append(fund_result)
    
    report = generate_report(portfolio_name, portfolio_id, len(funds), results, comparisons)
    
    return {
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio_name,
        'fund_count': len(funds),
        'success_count': success_count,
        'skip_count': skip_count,
        'results': results,
        'comparisons': comparisons,
        'report': report
    }


def generate_report(portfolio_name: str, portfolio_id: int, 
                    total: int, results: List, comparisons: List) -> str:
    """
    生成执行报告
    """
    lines = []
    lines.append("=" * 70)
    lines.append("风险指标计算报告")
    lines.append("=" * 70)
    lines.append(f"计算时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"组合: {portfolio_name} (ID: {portfolio_id})")
    lines.append(f"基金总数: {total}")
    lines.append("")
    
    success_list = []
    skip_list = []
    
    for r in results:
        for p in r['periods']:
            if p['success']:
                data = p['data']
                success_list.append({
                    'code': r['fund_code'],
                    'name': r['fund_name'],
                    'period': p['period'],
                    'dd': data.get('max_drawdown'),
                    'vol': data.get('annual_volatility'),
                    'sharpe': data.get('sharpe_ratio')
                })
            else:
                skip_list.append({
                    'code': r['fund_code'],
                    'name': r['fund_name'],
                    'period': p['period'],
                    'error': p.get('error')
                })
    
    lines.append(f"计算结果:")
    lines.append(f"  成功: {len(success_list)} 个")
    lines.append(f"  跳过: {len(skip_list)} 个")
    lines.append("")
    
    if success_list:
        lines.append("成功列表:")
        for s in success_list:
            dd = f"{s['dd']:.2f}%" if s['dd'] else '-'
            vol = f"{s['vol']:.2f}%" if s['vol'] else '-'
            sharpe = f"{s['sharpe']:.2f}" if s['sharpe'] else '-'
            lines.append(f"  {s['code']} {s['name']} - {s['period']}: 回撤{dd}, 波动率{vol}, 夏普{sharpe}")
        lines.append("")
    
    if skip_list:
        lines.append("跳过列表:")
        for s in skip_list:
            lines.append(f"  {s['code']} {s['name']} - {s['period']}: {s['error']}")
        lines.append("")
    
    consistent = [c for c in comparisons if c.get('is_consistent')]
    inconsistent = [c for c in comparisons if not c.get('is_consistent')]
    
    lines.append(f"对比结果（自计算 vs 雪球）:")
    lines.append(f"  一致: {len(consistent)} 个")
    lines.append(f"  不一致: {len(inconsistent)} 个")
    
    if inconsistent:
        for c in inconsistent:
            lines.append(f"    - {c['fund_code']} {c['period']}: {', '.join(c['issues'])}")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)
