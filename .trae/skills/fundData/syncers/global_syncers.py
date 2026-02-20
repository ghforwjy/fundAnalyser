"""
全局数据同步器
批量同步全市场基金数据
"""
import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from funddb import get_db_connection, update_sync_meta


class SyncResult:
    """同步结果"""
    def __init__(self, success: bool, message: str, record_count: int = 0, errors: List[str] = None):
        self.success = success
        self.message = message
        self.record_count = record_count
        self.errors = errors or []


def sync_fund_info() -> SyncResult:
    """
    同步基金基本信息（批量）
    使用AKShare的fund_name_em接口获取全市场基金列表
    """
    print("[FundData] 开始同步基金基本信息...")
    
    try:
        # 获取基金列表
        df = ak.fund_name_em()
        
        if df is None or len(df) == 0:
            return SyncResult(False, "未获取到基金数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 只基金")
        
        # 获取基金公司映射
        company_map = {}
        try:
            df_rating = ak.fund_rating_all()
            if df_rating is not None:
                for _, row in df_rating.iterrows():
                    fund_code = str(row.get('代码', '')).strip()
                    company = str(row.get('基金公司', '')).strip()
                    if fund_code and company:
                        company_map[fund_code] = company
        except Exception as e:
            print(f"[FundData] 获取基金公司信息失败: {e}")
        
        # 准备数据
        data = []
        for _, row in df.iterrows():
            fund_code = str(row.get('基金代码', '')).strip()
            fund_name = str(row.get('基金简称', '')).strip()
            fund_type = str(row.get('基金类型', '')).strip()
            
            data.append({
                'fund_code': fund_code,
                'fund_name': fund_name,
                'fund_full_name': fund_name,
                'fund_type': fund_type,
                'pinyin_abbr': str(row.get('拼音缩写', '')).strip(),
                'pinyin_full': str(row.get('拼音全称', '')).strip(),
                'company_name': company_map.get(fund_code, ''),
                'data_source': 'akshare'
            })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 使用INSERT OR REPLACE批量插入
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['fund_name'], item['fund_full_name'],
                    item['fund_type'], item['pinyin_abbr'], item['pinyin_full'],
                    item['company_name'], item['data_source']
                ))
            
            # 分批插入
            batch_size = 500
            for i in range(0, len(insert_values), batch_size):
                batch = insert_values[i:i+batch_size]
                cursor.executemany('''
                    INSERT OR REPLACE INTO fund_info 
                    (fund_code, fund_name, fund_full_name, fund_type, pinyin_abbr, pinyin_full,
                     company_name, data_source, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', batch)
            
            conn.commit()
        
        # 更新元数据
        update_sync_meta('fund_info', 'success')
        
        has_company = sum(1 for item in data if item['company_name'])
        print(f"[FundData] 基金基本信息同步完成: {len(data)} 只基金")
        
        return SyncResult(
            True, 
            f"成功同步 {len(data)} 只基金基本信息（{has_company} 只有基金公司信息）",
            len(data)
        )
        
    except Exception as e:
        error_msg = f"同步基金基本信息失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_info', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_fund_rating() -> SyncResult:
    """
    同步基金评级数据（批量）
    使用AKShare的fund_rating_all接口
    """
    print("[FundData] 开始同步基金评级数据...")
    
    try:
        df = ak.fund_rating_all()
        
        if df is None or len(df) == 0:
            return SyncResult(False, "未获取到评级数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 条评级记录")
        
        data = []
        for _, row in df.iterrows():
            fund_code = str(row.get('代码', '')).strip()
            if not fund_code:
                continue
                
            data.append({
                'fund_code': fund_code,
                'fund_name': str(row.get('简称', '')).strip(),
                'manager_name': str(row.get('基金经理', '')).strip(),
                'company_name': str(row.get('基金公司', '')).strip(),
                'rating_5star_count': int(row.get('5星评级家数', 0)) if pd.notna(row.get('5星评级家数')) else 0,
                'rating_sh': float(row.get('上海证券评级', 0)) if pd.notna(row.get('上海证券评级')) else None,
                'rating_zs': float(row.get('招商证券评级', 0)) if pd.notna(row.get('招商证券评级')) else None,
                'rating_ja': float(row.get('济安金信评级', 0)) if pd.notna(row.get('济安金信评级')) else None,
                'rating_morningstar': float(row.get('晨星评级', 0)) if pd.notna(row.get('晨星评级')) else None,
                'fee_rate': float(row.get('手续费', 0)) if pd.notna(row.get('手续费')) else None,
                'fund_type': str(row.get('类型', '')).strip()
            })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['fund_name'], item['manager_name'],
                    item['company_name'], item['rating_5star_count'], item['rating_sh'],
                    item['rating_zs'], item['rating_ja'], item['rating_morningstar'],
                    item['fee_rate'], item['fund_type']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_rating
                (fund_code, fund_name, manager_name, company_name, rating_5star_count,
                 rating_sh, rating_zs, rating_ja, rating_morningstar, fee_rate, fund_type, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        update_sync_meta('fund_rating', 'success')
        print(f"[FundData] 基金评级数据同步完成: {len(data)} 条记录")
        
        return SyncResult(True, f"成功同步 {len(data)} 条基金评级数据", len(data))
        
    except Exception as e:
        error_msg = f"同步基金评级数据失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_rating', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_fund_manager() -> SyncResult:
    """
    同步基金经理数据（批量）
    使用AKShare的fund_manager_em接口
    """
    print("[FundData] 开始同步基金经理数据...")
    
    try:
        df = ak.fund_manager_em()
        
        if df is None or len(df) == 0:
            return SyncResult(False, "未获取到基金经理数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 位基金经理")
        
        data = []
        for _, row in df.iterrows():
            manager_name = str(row.get('姓名', '')).strip()
            if not manager_name:
                continue
            
            # 解析现任基金代码和名称
            fund_codes = str(row.get('现任基金代码', '')).strip().split(',')
            fund_names = str(row.get('现任基金', '')).strip().split(',')
            
            for i, fund_code in enumerate(fund_codes):
                fund_code = fund_code.strip()
                if not fund_code:
                    continue
                    
                fund_name = fund_names[i].strip() if i < len(fund_names) else ''
                
                data.append({
                    'manager_name': manager_name,
                    'company_name': str(row.get('所属公司', '')).strip(),
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'tenure_days': int(row.get('累计从业时间', 0)) if pd.notna(row.get('累计从业时间')) else 0,
                    'total_scale': float(row.get('现任基金资产总规模', 0)) if pd.notna(row.get('现任基金资产总规模')) else 0,
                    'best_return': float(row.get('现任基金最佳回报', 0)) if pd.notna(row.get('现任基金最佳回报')) else 0
                })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['manager_name'], item['company_name'], item['fund_code'],
                    item['fund_name'], item['tenure_days'], item['total_scale'],
                    item['best_return']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_manager
                (manager_name, company_name, fund_code, fund_name, tenure_days, total_scale, best_return, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        update_sync_meta('fund_manager', 'success')
        print(f"[FundData] 基金经理数据同步完成: {len(data)} 条记录")
        
        return SyncResult(True, f"成功同步 {len(data)} 条基金经理数据", len(data))
        
    except Exception as e:
        error_msg = f"同步基金经理数据失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_manager', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_fund_company() -> SyncResult:
    """
    同步基金公司数据（批量）
    
    注意：AKShare的fund_company_em接口可能不可用
    基金公司信息可从fund_manager表中提取
    """
    print("[FundData] 开始同步基金公司数据...")
    
    try:
        if not hasattr(ak, 'fund_company_em'):
            print("[FundData] fund_company_em接口不可用，从基金经理数据中提取公司信息")
            return _sync_fund_company_from_manager()
        
        df = ak.fund_company_em()
        
        if df is None or len(df) == 0:
            return SyncResult(False, "未获取到基金公司数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 家基金公司")
        
        data = []
        for _, row in df.iterrows():
            company_name = str(row.get('基金公司', '')).strip()
            if not company_name:
                continue
            
            data.append({
                'company_name': company_name,
                'establish_date': str(row.get('成立日期', '')).strip() or None,
                'manage_scale': float(row.get('管理规模', 0)) if pd.notna(row.get('管理规模')) else 0,
                'fund_count': int(row.get('基金数量', 0)) if pd.notna(row.get('基金数量')) else 0,
                'manager_count': int(row.get('经理人数', 0)) if pd.notna(row.get('经理人数')) else 0,
                'rating_tx': int(row.get('天相评级', 0)) if pd.notna(row.get('天相评级')) else None,
                'description': str(row.get('简介', '')).strip()
            })
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['company_name'], item['establish_date'], item['manage_scale'],
                    item['fund_count'], item['manager_count'], item['rating_tx'],
                    item['description']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_company
                (company_name, establish_date, manage_scale, fund_count, manager_count, rating_tx, description, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        update_sync_meta('fund_company', 'success')
        print(f"[FundData] 基金公司数据同步完成: {len(data)} 家")
        
        return SyncResult(True, f"成功同步 {len(data)} 家基金公司数据", len(data))
        
    except Exception as e:
        error_msg = f"同步基金公司数据失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_company', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def _sync_fund_company_from_manager() -> SyncResult:
    """
    从基金经理数据中提取基金公司信息
    作为fund_company_em接口不可用时的备选方案
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT company_name, COUNT(DISTINCT manager_name) as manager_count
                FROM fund_manager
                WHERE company_name IS NOT NULL AND company_name != ''
                GROUP BY company_name
            ''')
            
            rows = cursor.fetchall()
            
            if not rows:
                return SyncResult(False, "基金经理表中无公司信息")
            
            data = []
            for row in rows:
                data.append({
                    'company_name': row['company_name'],
                    'manager_count': row['manager_count']
                })
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_company
                (company_name, manager_count, update_time)
                VALUES (?, ?, datetime('now'))
            ''', [(d['company_name'], d['manager_count']) for d in data])
            
            conn.commit()
        
        update_sync_meta('fund_company', 'success')
        print(f"[FundData] 从基金经理数据提取公司信息完成: {len(data)} 家")
        
        return SyncResult(True, f"成功提取 {len(data)} 家基金公司信息", len(data))
        
    except Exception as e:
        error_msg = f"从基金经理数据提取公司信息失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_fund_dividend(year: str = None) -> SyncResult:
    """
    同步基金分红数据（批量）
    使用AKShare的fund_fh_em接口
    
    Args:
        year: 年份，如 "2025"，不传则同步当年
    """
    if not year:
        year = str(datetime.now().year)
    
    print(f"[FundData] 开始同步 {year} 年基金分红数据...")
    
    try:
        df = ak.fund_fh_em(year=year)
        
        if df is None or len(df) == 0:
            return SyncResult(False, f"未获取到 {year} 年分红数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 条分红记录")
        
        data = []
        for _, row in df.iterrows():
            fund_code = str(row.get('基金代码', '')).strip()
            if not fund_code:
                continue
            
            data.append({
                'fund_code': fund_code,
                'fund_name': str(row.get('基金简称', '')).strip(),
                'record_date': str(row.get('权益登记日', '')).strip() or None,
                'ex_dividend_date': str(row.get('除息日期', '')).strip() or None,
                'dividend_per_share': float(row.get('分红', 0)) if pd.notna(row.get('分红')) else 0,
                'payment_date': str(row.get('分红发放日', '')).strip() or None,
                'year': year
            })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['fund_name'], item['record_date'],
                    item['ex_dividend_date'], item['dividend_per_share'],
                    item['payment_date'], item['year']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_dividend
                (fund_code, fund_name, record_date, ex_dividend_date, dividend_per_share, payment_date, year, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        update_sync_meta('fund_dividend', 'success')
        print(f"[FundData] 基金分红数据同步完成: {len(data)} 条记录")
        
        return SyncResult(True, f"成功同步 {len(data)} 条 {year} 年基金分红数据", len(data))
        
    except Exception as e:
        error_msg = f"同步基金分红数据失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_dividend', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_fund_split(year: str = None) -> SyncResult:
    """
    同步基金拆分数据（批量）
    使用AKShare的fund_cf_em接口
    
    Args:
        year: 年份，如 "2025"，不传则同步当年
    """
    if not year:
        year = str(datetime.now().year)
    
    print(f"[FundData] 开始同步 {year} 年基金拆分数据...")
    
    try:
        df = ak.fund_cf_em(year=year)
        
        if df is None or len(df) == 0:
            return SyncResult(False, f"未获取到 {year} 年拆分数据")
        
        print(f"[FundData] 从AKShare获取到 {len(df)} 条拆分记录")
        
        data = []
        for _, row in df.iterrows():
            fund_code = str(row.get('基金代码', '')).strip()
            if not fund_code:
                continue
            
            data.append({
                'fund_code': fund_code,
                'fund_name': str(row.get('基金简称', '')).strip(),
                'split_date': str(row.get('拆分折算日', '')).strip() or None,
                'split_type': str(row.get('拆分类型', '')).strip(),
                'split_ratio': float(row.get('拆分折算', 0)) if pd.notna(row.get('拆分折算')) else 0,
                'year': year
            })
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            insert_values = []
            for item in data:
                insert_values.append((
                    item['fund_code'], item['fund_name'], item['split_date'],
                    item['split_type'], item['split_ratio'], item['year']
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO fund_split
                (fund_code, fund_name, split_date, split_type, split_ratio, year, update_time)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', insert_values)
            
            conn.commit()
        
        update_sync_meta('fund_split', 'success')
        print(f"[FundData] 基金拆分数据同步完成: {len(data)} 条记录")
        
        return SyncResult(True, f"成功同步 {len(data)} 条 {year} 年基金拆分数据", len(data))
        
    except Exception as e:
        error_msg = f"同步基金拆分数据失败: {str(e)}"
        print(f"[FundData] {error_msg}")
        update_sync_meta('fund_split', 'failed', str(e))
        return SyncResult(False, error_msg, errors=[str(e)])


def sync_all_global_data() -> Dict[str, SyncResult]:
    """
    同步所有全局数据
    """
    print("=" * 60)
    print("[FundData] 开始同步所有全局数据")
    print("=" * 60)
    
    results = {}
    
    # 1. 基金基本信息（必须先同步，其他数据依赖它）
    results['fund_info'] = sync_fund_info()
    time.sleep(1)
    
    # 2. 基金评级
    results['fund_rating'] = sync_fund_rating()
    time.sleep(1)
    
    # 3. 基金经理
    results['fund_manager'] = sync_fund_manager()
    time.sleep(1)
    
    # 4. 基金公司
    results['fund_company'] = sync_fund_company()
    time.sleep(1)
    
    # 5. 基金分红（当年）
    results['fund_dividend'] = sync_fund_dividend()
    time.sleep(1)
    
    # 6. 基金拆分（当年）
    results['fund_split'] = sync_fund_split()
    
    print("=" * 60)
    print("[FundData] 全局数据同步完成")
    print("=" * 60)
    
    # 统计结果
    success_count = sum(1 for r in results.values() if r.success)
    total_count = len(results)
    
    print(f"\n同步结果统计:")
    for name, result in results.items():
        status = "✓" if result.success else "✗"
        print(f"  {status} {name}: {result.message}")
    
    print(f"\n总计: {success_count}/{total_count} 项同步成功")
    
    return results
