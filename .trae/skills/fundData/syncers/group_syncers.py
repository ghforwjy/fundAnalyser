"""
分组数据同步器
按需获取指定基金代码的详细数据
"""
import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from funddb import get_db_connection, update_sync_meta


# 跳过行业配置查询的基金类型（这些基金没有股票行业配置）
SKIP_INDUSTRY_ALLOCATION_TYPES = [
    '债券型-混合一级',
    '债券型-长债',
    '债券型-中短债',
    '债券型-可转债',
    '指数型-其他',
    '货币型',
]


class SyncResult:
    """同步结果"""
    def __init__(self, success: bool, message: str, record_count: int = 0, errors: List[str] = None):
        self.success = success
        self.message = message
        self.record_count = record_count
        self.errors = errors or []


def validate_fund_codes(fund_codes: List[str]) -> List[str]:
    """
    验证基金代码是否存在于fund_info表中
    """
    valid_codes = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for code in fund_codes:
            cursor.execute("SELECT 1 FROM fund_info WHERE fund_code = ?", (code,))
            if cursor.fetchone():
                valid_codes.append(code)
            else:
                print(f"[FundData] 警告: 基金代码 {code} 不存在于fund_info表中")
    return valid_codes


def sync_single_fund_nav(fund_code: str) -> Dict[str, Any]:
    """
    同步单只基金的历史净值
    使用AKShare的fund_open_fund_info_em接口
    """
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        
        if df is None or len(df) == 0:
            return {'success': False, 'code': fund_code, 'error': '无数据', 'count': 0}
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'fund_code': fund_code,
                'nav_date': str(row.get('净值日期', '')).strip(),
                'unit_nav': float(row.get('单位净值', 0)) if pd.notna(row.get('单位净值')) else None,
                'accum_nav': float(row.get('累计净值', 0)) if pd.notna(row.get('累计净值')) else None,
                'daily_return': float(row.get('日增长率', 0)) if pd.notna(row.get('日增长率')) else None
            })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['nav_date'], item['unit_nav'],
                    item['accum_nav'], item['daily_return']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_nav
                (fund_code, nav_date, unit_nav, accum_nav, daily_return, update_time)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        return {'success': True, 'code': fund_code, 'count': len(data)}
        
    except Exception as e:
        return {'success': False, 'code': fund_code, 'error': str(e), 'count': 0}


def sync_group_nav(fund_codes: List[str], max_workers: int = 3) -> SyncResult:
    """
    同步分组基金的历史净值（单只获取，并发执行）
    
    Args:
        fund_codes: 基金代码列表
        max_workers: 并发线程数（避免请求过于频繁）
    """
    print(f"[FundData] 开始同步 {len(fund_codes)} 只基金的历史净值...")
    
    # 验证基金代码
    valid_codes = validate_fund_codes(fund_codes)
    if not valid_codes:
        return SyncResult(False, "没有有效的基金代码", 0)
    
    print(f"[FundData] 有效基金代码: {len(valid_codes)} 只")
    
    results = []
    total_count = 0
    
    # 并发获取数据
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(sync_single_fund_nav, code): code for code in valid_codes}
        
        for future in as_completed(future_to_code):
            result = future.result()
            results.append(result)
            
            if result['success']:
                total_count += result['count']
                print(f"[FundData] ✓ {result['code']}: {result['count']} 条净值数据")
            else:
                print(f"[FundData] ✗ {result['code']}: {result['error']}")
            
            # 添加延迟避免频率限制
            time.sleep(0.5)
    
    success_count = sum(1 for r in results if r['success'])
    
    # 更新元数据
    update_sync_meta('fund_nav', 'success' if success_count > 0 else 'partial')
    
    message = f"成功同步 {success_count}/{len(valid_codes)} 只基金净值数据，共 {total_count} 条记录"
    print(f"[FundData] {message}")
    
    return SyncResult(
        success_count > 0,
        message,
        total_count,
        [r['error'] for r in results if not r['success']]
    )


def sync_single_fund_holding(fund_code: str, years: List[str] = None) -> Dict[str, Any]:
    """
    同步单只基金的持仓数据（股票、债券、行业）
    
    Args:
        fund_code: 基金代码
        years: 年份列表，如['2024', '2025']，默认获取当年和去年
    """
    if not years:
        current_year = datetime.now().year
        years = [str(current_year), str(current_year - 1)]
    
    results = {'success': True, 'code': fund_code, 'stock_count': 0, 'bond_count': 0, 'industry_count': 0}
    errors = []
    
    # 创建日志文件（使用绝对路径）
    import os
    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建log目录的绝对路径（在fundData目录下）
    fund_data_dir = os.path.dirname(current_dir)
    log_dir = os.path.join(fund_data_dir, 'log')
    # 确保log目录存在
    os.makedirs(log_dir, exist_ok=True)
    # 构建日志文件的绝对路径
    log_file = os.path.join(log_dir, f"holdings_sync_error_{datetime.now().strftime('%Y%m%d')}.log")
    
    def log_error(message):
        """记录错误到日志文件"""
        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{error_time}] {message}\n"
        print(log_message.strip())
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
    
    for year in years:
        try:
            # 1. 股票持仓
            try:
                df_stock = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
                if df_stock is not None and len(df_stock) > 0:
                    data = []
                    for _, row in df_stock.iterrows():
                        hold_ratio_str = str(row.get('占净值比例', '0')).strip()
                        try:
                            hold_ratio = float(hold_ratio_str) if hold_ratio_str and hold_ratio_str != '' else 0
                        except:
                            hold_ratio = 0
                        
                        data.append({
                            'fund_code': fund_code,
                            'report_date': str(row.get('季度', '')).strip(),
                            'stock_code': str(row.get('股票代码', '')).strip(),
                            'stock_name': str(row.get('股票名称', '')).strip(),
                            'hold_ratio': hold_ratio,
                            'hold_shares': float(row.get('持股数', 0)) if pd.notna(row.get('持股数')) else 0,
                            'hold_value': float(row.get('持仓市值', 0)) if pd.notna(row.get('持仓市值')) else 0,
                            'quarter': str(row.get('季度', '')).strip()
                        })
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        insert_values = [(d['fund_code'], d['report_date'], d['stock_code'], 
                                         d['stock_name'], d['hold_ratio'], d['hold_shares'], 
                                         d['hold_value'], d['quarter']) for d in data]
                        
                        cursor.executemany('''
                            INSERT OR REPLACE INTO fund_stock_holding
                            (fund_code, report_date, stock_code, stock_name, hold_ratio, hold_shares, hold_value, quarter, update_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        ''', insert_values)
                        conn.commit()
                    
                    results['stock_count'] += len(data)
            except Exception as e:
                error_msg = f"获取 {fund_code} {year}年股票持仓失败: {e}"
                log_error(error_msg)
                errors.append(error_msg)
        
            # 2. 债券持仓
            try:
                df_bond = ak.fund_portfolio_bond_hold_em(symbol=fund_code, date=year)
                if df_bond is not None and len(df_bond) > 0:
                    data = []
                    for _, row in df_bond.iterrows():
                        hold_ratio_str = str(row.get('占净值比例', '0')).strip()
                        try:
                            hold_ratio = float(hold_ratio_str) if hold_ratio_str and hold_ratio_str != '' else 0
                        except:
                            hold_ratio = 0
                        
                        data.append({
                            'fund_code': fund_code,
                            'report_date': str(row.get('季度', '')).strip(),
                            'bond_code': str(row.get('债券代码', '')).strip(),
                            'bond_name': str(row.get('债券名称', '')).strip(),
                            'hold_ratio': hold_ratio,
                            'hold_value': float(row.get('持仓市值', 0)) if pd.notna(row.get('持仓市值')) else 0,
                            'quarter': str(row.get('季度', '')).strip()
                        })
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        insert_values = [(d['fund_code'], d['report_date'], d['bond_code'], 
                                         d['bond_name'], d['hold_ratio'], d['hold_value'], d['quarter']) for d in data]
                        
                        cursor.executemany('''
                            INSERT OR REPLACE INTO fund_bond_holding
                            (fund_code, report_date, bond_code, bond_name, hold_ratio, hold_value, quarter, update_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        ''', insert_values)
                        conn.commit()
                    
                    results['bond_count'] += len(data)
            except Exception as e:
                error_msg = f"获取 {fund_code} {year}年债券持仓失败: {e}"
                log_error(error_msg)
                errors.append(error_msg)
            
            # 3. 行业配置（某些基金类型跳过）
            # 获取基金类型
            fund_type = None
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT fund_type FROM fund_info WHERE fund_code = ?", (fund_code,))
                row = cursor.fetchone()
                if row:
                    fund_type = row['fund_type']
            
            # 检查是否需要跳过行业配置查询
            skip_industry = False
            if fund_type:
                for skip_type in SKIP_INDUSTRY_ALLOCATION_TYPES:
                    if skip_type in fund_type:
                        skip_industry = True
                        break
            
            if not skip_industry:
                try:
                    df_industry = ak.fund_portfolio_industry_allocation_em(symbol=fund_code, date=year)
                    if df_industry is not None and len(df_industry) > 0:
                        data = []
                        for _, row in df_industry.iterrows():
                            alloc_ratio_str = str(row.get('占净值比例', '0')).strip()
                            try:
                                alloc_ratio = float(alloc_ratio_str) if alloc_ratio_str and alloc_ratio_str != '' else 0
                            except:
                                alloc_ratio = 0
                            
                            data.append({
                                'fund_code': fund_code,
                                'report_date': str(row.get('截止时间', '')).strip(),
                                'industry_name': str(row.get('行业类别', '')).strip(),
                                'allocation_ratio': alloc_ratio,
                                'market_value': float(row.get('市值', 0)) if pd.notna(row.get('市值')) else 0,
                                'quarter': str(row.get('截止时间', '')).strip()
                            })
                        
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            insert_values = [(d['fund_code'], d['report_date'], d['industry_name'], 
                                             d['allocation_ratio'], d['market_value'], d['quarter']) for d in data]
                            
                            cursor.executemany('''
                                INSERT OR REPLACE INTO fund_industry_allocation
                                (fund_code, report_date, industry_name, allocation_ratio, market_value, quarter, update_time)
                                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                            ''', insert_values)
                            conn.commit()
                        
                        results['industry_count'] += len(data)
                except Exception as e:
                    error_msg = f"获取 {fund_code} {year}年行业配置失败: {e}"
                    log_error(error_msg)
                    errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"获取 {fund_code} {year}年数据失败: {e}"
            log_error(error_msg)
            errors.append(error_msg)
    
    # 无论成功还是失败，都记录到fund_data_meta表，标记为当天查询过
    from funddb import update_holdings_meta
    if errors:
        results['success'] = False
        update_holdings_meta(fund_code, 'failed')
    else:
        update_holdings_meta(fund_code, 'success')
    
    return results


def sync_group_holdings(fund_codes: List[str], years: List[str] = None, max_workers: int = 3) -> SyncResult:
    """
    同步分组基金的持仓数据
    
    Args:
        fund_codes: 基金代码列表
        years: 年份列表，默认当年和去年
        max_workers: 并发线程数
    """
    if not years:
        current_year = datetime.now().year
        years = [str(current_year), str(current_year - 1)]
    
    print(f"[FundData] 开始同步 {len(fund_codes)} 只基金的持仓数据（{years}年）...")
    
    valid_codes = validate_fund_codes(fund_codes)
    if not valid_codes:
        return SyncResult(False, "没有有效的基金代码", 0)
    
    results = []
    total_stock = 0
    total_bond = 0
    total_industry = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(sync_single_fund_holding, code, years): code for code in valid_codes}
        
        for future in as_completed(future_to_code):
            result = future.result()
            results.append(result)
            
            if result['success']:
                total_stock += result['stock_count']
                total_bond += result['bond_count']
                total_industry += result['industry_count']
                print(f"[FundData] ✓ {result['code']}: 股票{result['stock_count']} 债券{result['bond_count']} 行业{result['industry_count']}")
            else:
                print(f"[FundData] ✗ {result['code']}: {result.get('error', '未知错误')}")
            
            time.sleep(0.5)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = total_stock + total_bond + total_industry
    
    update_sync_meta('fund_stock_holding', 'success' if success_count > 0 else 'partial')
    
    message = f"成功同步 {success_count}/{len(valid_codes)} 只基金持仓数据（股票{total_stock} 债券{total_bond} 行业{total_industry}）"
    print(f"[FundData] {message}")
    
    return SyncResult(success_count > 0, message, total_count)


def sync_single_fund_risk(fund_code: str) -> Dict[str, Any]:
    """
    同步单只基金的风险指标
    使用AKShare的fund_individual_analysis_xq接口
    
    数据来源：蛋卷基金API
    返回字段：
    - 周期：近1年、近3年、近5年
    - 较同类风险收益比：综合统计基金承担风险获取收益的性价比排名
    - 较同类抗风险波动：综合统计基金抗风险波动能力排名
    - 年化波动率：基金的年化波动幅度，数值越小波动越小
    - 年化夏普比率：每承受一单位总风险产生的超额收益，数值越大越好
    - 最大回撤：净值走到最低点时的收益率回撤幅度最大值
    """
    try:
        df = ak.fund_individual_analysis_xq(symbol=fund_code)
        
        if df is None or len(df) == 0:
            return {'success': False, 'code': fund_code, 'error': '无数据', 'count': 0}
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'fund_code': fund_code,
                'period': str(row.get('周期', '')).strip(),
                'risk_return_ratio': int(row.get('较同类风险收益比', 0)) if pd.notna(row.get('较同类风险收益比')) else None,
                'risk_resistance': int(row.get('较同类抗风险波动', 0)) if pd.notna(row.get('较同类抗风险波动')) else None,
                'annual_volatility': float(row.get('年化波动率', 0)) if pd.notna(row.get('年化波动率')) else None,
                'sharpe_ratio': float(row.get('年化夏普比率', 0)) if pd.notna(row.get('年化夏普比率')) else None,
                'max_drawdown': float(row.get('最大回撤', 0)) if pd.notna(row.get('最大回撤')) else None
            })
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['period'], item['risk_return_ratio'],
                    item['risk_resistance'], item['annual_volatility'],
                    item['sharpe_ratio'], item['max_drawdown']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_risk_metrics
                (fund_code, period, risk_return_ratio, risk_resistance, annual_volatility, sharpe_ratio, max_drawdown, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        return {'success': True, 'code': fund_code, 'count': len(data)}
        
    except KeyError as e:
        if 'index_data_list' in str(e) or 'index_time_period' in str(e):
            return {'success': False, 'code': fund_code, 'error': '该基金无风险指标数据(可能成立时间较短)', 'count': 0}
        return {'success': False, 'code': fund_code, 'error': f'字段缺失: {str(e)}', 'count': 0}
    except Exception as e:
        return {'success': False, 'code': fund_code, 'error': str(e), 'count': 0}


def sync_group_risk_metrics(fund_codes: List[str], max_workers: int = 3) -> SyncResult:
    """
    同步分组基金的风险指标
    """
    print(f"[FundData] 开始同步 {len(fund_codes)} 只基金的风险指标...")
    
    valid_codes = validate_fund_codes(fund_codes)
    if not valid_codes:
        return SyncResult(False, "没有有效的基金代码", 0)
    
    results = []
    total_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(sync_single_fund_risk, code): code for code in valid_codes}
        
        for future in as_completed(future_to_code):
            result = future.result()
            results.append(result)
            
            if result['success']:
                total_count += result['count']
                print(f"[FundData] ✓ {result['code']}: {result['count']} 条风险指标")
            else:
                print(f"[FundData] ✗ {result['code']}: {result['error']}")
            
            time.sleep(0.5)
    
    success_count = sum(1 for r in results if r['success'])
    
    update_sync_meta('fund_risk_metrics', 'success' if success_count > 0 else 'partial')
    
    message = f"成功同步 {success_count}/{len(valid_codes)} 只基金风险指标，共 {total_count} 条记录"
    print(f"[FundData] {message}")
    
    return SyncResult(success_count > 0, message, total_count)


def sync_single_fund_performance(fund_code: str) -> Dict[str, Any]:
    """
    同步单只基金的业绩表现
    使用AKShare的fund_individual_achievement_xq接口
    """
    try:
        df = ak.fund_individual_achievement_xq(symbol=fund_code)
        
        if df is None or len(df) == 0:
            return {'success': False, 'code': fund_code, 'error': '无数据', 'count': 0}
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'fund_code': fund_code,
                'performance_type': str(row.get('业绩类型', '')).strip(),
                'period': str(row.get('周期', '')).strip(),
                'period_return': float(row.get('本产品区间收益', 0)) if pd.notna(row.get('本产品区间收益')) else None,
                'max_drawdown': float(row.get('本产品最大回撤', 0)) if pd.notna(row.get('本产品最大回撤')) else None,
                'rank_in_category': str(row.get('周期收益同类排名', '')).strip()
            })
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['performance_type'], item['period'],
                    item['period_return'], item['max_drawdown'], item['rank_in_category']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_performance
                (fund_code, performance_type, period, period_return, max_drawdown, rank_in_category, update_time)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        return {'success': True, 'code': fund_code, 'count': len(data)}
        
    except Exception as e:
        return {'success': False, 'code': fund_code, 'error': str(e), 'count': 0}


def sync_group_performance(fund_codes: List[str], max_workers: int = 3) -> SyncResult:
    """
    同步分组基金的业绩表现
    """
    print(f"[FundData] 开始同步 {len(fund_codes)} 只基金的业绩表现...")
    
    valid_codes = validate_fund_codes(fund_codes)
    if not valid_codes:
        return SyncResult(False, "没有有效的基金代码", 0)
    
    results = []
    total_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(sync_single_fund_performance, code): code for code in valid_codes}
        
        for future in as_completed(future_to_code):
            result = future.result()
            results.append(result)
            
            if result['success']:
                total_count += result['count']
                print(f"[FundData] ✓ {result['code']}: {result['count']} 条业绩数据")
            else:
                print(f"[FundData] ✗ {result['code']}: {result['error']}")
            
            time.sleep(0.5)
    
    success_count = sum(1 for r in results if r['success'])
    
    update_sync_meta('fund_performance', 'success' if success_count > 0 else 'partial')
    
    message = f"成功同步 {success_count}/{len(valid_codes)} 只基金业绩表现，共 {total_count} 条记录"
    print(f"[FundData] {message}")
    
    return SyncResult(success_count > 0, message, total_count)


def sync_group_all_data(fund_codes: List[str], year: str = None) -> Dict[str, SyncResult]:
    """
    同步分组的所有数据（净值、持仓、风险、业绩）
    
    Args:
        fund_codes: 基金代码列表
        year: 持仓数据年份
    """
    print("=" * 60)
    print(f"[FundData] 开始同步分组所有数据: {len(fund_codes)} 只基金")
    print("=" * 60)
    
    results = {}
    
    # 1. 历史净值
    results['fund_nav'] = sync_group_nav(fund_codes)
    time.sleep(2)
    
    # 2. 持仓数据
    results['fund_holdings'] = sync_group_holdings(fund_codes, year)
    time.sleep(2)
    
    # 3. 风险指标
    results['fund_risk'] = sync_group_risk_metrics(fund_codes)
    time.sleep(2)
    
    # 4. 业绩表现
    results['fund_performance'] = sync_group_performance(fund_codes)
    
    print("=" * 60)
    print("[FundData] 分组数据同步完成")
    print("=" * 60)
    
    return results
