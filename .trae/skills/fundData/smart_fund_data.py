"""
智能基金数据管理模块
提供通用查询接口和智能缓存机制
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill
from funddb import get_db_connection
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import time

from value_averaging import ValueAveragingCalculator, calculate_value_averaging, get_value_averaging_report


class SmartFundData:
    """
    智能基金数据管理类
    
    特性：
    1. 优先从本地数据库查询
    2. 自动检查数据新鲜度
    3. 智能判断是否需要重新获取
    4. 提供通用灵活的查询接口
    """
    
    def __init__(self):
        self.skill = FundDataSkill()
    
    # ==================== 通用查询接口 ====================
    
    def query_funds(self, 
                   keyword: str = None,
                   fund_type: str = None,
                   company: str = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        通用基金查询接口
        
        Args:
            keyword: 关键词（代码/名称/拼音）
            fund_type: 基金类型筛选
            company: 基金公司筛选
            limit: 返回数量限制
        
        Returns:
            基金列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT fund_code, fund_name, fund_type, company_name, 
                       pinyin_abbr, establish_date, update_time
                FROM fund_info
                WHERE 1=1
            '''
            params = []
            
            if keyword:
                query += ''' AND (
                    fund_code LIKE ? OR 
                    fund_name LIKE ? OR 
                    pinyin_abbr LIKE ? OR
                    pinyin_full LIKE ?
                )'''
                pattern = f"%{keyword}%"
                params.extend([pattern, pattern, pattern, pattern])
            
            if fund_type:
                query += ' AND fund_type LIKE ?'
                params.append(f"%{fund_type}%")
            
            if company:
                query += ' AND company_name LIKE ?'
                params.append(f"%{company}%")
            
            query += ' ORDER BY fund_code LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_latest_nav(self, 
                      fund_code: str,
                      force_update: bool = False,
                      max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        获取基金最新净值（智能缓存）
        
        Args:
            fund_code: 基金代码
            force_update: 是否强制更新
            max_age_hours: 数据最大有效期（小时）
        
        Returns:
            最新净值数据
        """
        # 检查是否需要更新
        need_update = force_update or self._is_nav_stale(fund_code, max_age_hours)
        
        if need_update:
            print(f"[SmartFund] 基金 {fund_code} 数据需要更新，正在获取最新数据...")
            self.skill.sync_group_nav([fund_code])
        else:
            print(f"[SmartFund] 基金 {fund_code} 使用本地缓存数据")
        
        # 从数据库查询
        nav_data = self.skill.query_fund_nav(fund_code, limit=1)
        return nav_data[0] if nav_data else None
    
    def get_funds_nav_list(self,
                          fund_codes: List[str] = None,
                          keyword: str = None,
                          fund_type: str = None,
                          company: str = None,
                          force_update: bool = False,
                          max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """
        批量获取基金最新净值列表（通用接口）
        
        Args:
            fund_codes: 指定基金代码列表
            keyword: 按关键词筛选
            fund_type: 按类型筛选
            company: 按公司筛选
            force_update: 是否强制更新
            max_age_hours: 数据最大有效期
        
        Returns:
            基金净值列表
        """
        # 如果没有指定代码，先查询符合条件的基金
        if not fund_codes:
            funds = self.query_funds(
                keyword=keyword,
                fund_type=fund_type,
                company=company,
                limit=100
            )
            fund_codes = [f['fund_code'] for f in funds]
        
        if not fund_codes:
            print("[SmartFund] 未找到符合条件的基金")
            return []
        
        print(f"[SmartFund] 准备获取 {len(fund_codes)} 只基金的最新净值")
        
        # 检查哪些需要更新
        codes_to_update = []
        for code in fund_codes:
            if force_update or self._is_nav_stale(code, max_age_hours):
                codes_to_update.append(code)
        
        # 批量更新需要更新的基金
        if codes_to_update:
            print(f"[SmartFund] {len(codes_to_update)} 只基金需要更新数据")
            self._batch_update_nav(codes_to_update)
        else:
            print(f"[SmartFund] 所有基金数据均为最新，使用本地缓存")
        
        # 查询所有基金的最新净值
        result = []
        for code in fund_codes:
            nav_data = self.skill.query_fund_nav(code, limit=1)
            fund_info = self._get_fund_info(code)
            
            if nav_data and fund_info:
                result.append({
                    'fund_code': code,
                    'fund_name': fund_info['fund_name'],
                    'fund_type': fund_info['fund_type'],
                    'company_name': fund_info['company_name'],
                    'nav_date': nav_data[0]['nav_date'],
                    'unit_nav': nav_data[0]['unit_nav'],
                    'accum_nav': nav_data[0]['accum_nav'],
                    'daily_return': nav_data[0]['daily_return']
                })
        
        return result
    
    def query_nav_history(self,
                         fund_code: str,
                         start_date: str = None,
                         end_date: str = None,
                         days: int = None,
                         ensure_data: bool = True) -> List[Dict[str, Any]]:
        """
        查询基金净值历史（通用接口）
        
        Args:
            fund_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期
            days: 最近N天
            ensure_data: 是否确保数据存在（不存在则获取）
        
        Returns:
            净值历史列表
        """
        # 如果需要确保数据存在
        if ensure_data:
            has_data = self._check_nav_exists(fund_code)
            if not has_data:
                print(f"[SmartFund] 基金 {fund_code} 无历史数据，正在获取...")
                self.skill.sync_group_nav([fund_code])
        
        # 计算日期范围
        if days and not start_date:
            end = datetime.now()
            start = end - timedelta(days=days)
            start_date = start.strftime('%Y-%m-%d')
            end_date = end.strftime('%Y-%m-%d')
        
        return self.skill.query_fund_nav(fund_code, start_date, end_date, limit=10000)
    
    def get_fund_detail_full(self, fund_code: str) -> Dict[str, Any]:
        """
        获取基金完整信息（基础信息+最新净值+评级等）
        
        Args:
            fund_code: 基金代码
        
        Returns:
            基金完整信息
        """
        result = {
            'fund_code': fund_code,
            'basic_info': None,
            'latest_nav': None,
            'rating': None,
            'manager': None
        }
        
        # 基础信息
        result['basic_info'] = self._get_fund_info(fund_code)
        
        # 最新净值
        nav_data = self.skill.query_fund_nav(fund_code, limit=1)
        if nav_data:
            result['latest_nav'] = nav_data[0]
        
        # 评级信息
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM fund_rating WHERE fund_code = ?
            ''', (fund_code,))
            row = cursor.fetchone()
            if row:
                result['rating'] = dict(row)
        
        # 基金经理
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM fund_manager WHERE fund_code = ? LIMIT 1
            ''', (fund_code,))
            row = cursor.fetchone()
            if row:
                result['manager'] = dict(row)
        
        return result
    
    # ==================== 智能更新机制 ====================
    
    def _is_nav_stale(self, fund_code: str, max_age_hours: int = 24) -> bool:
        """
        检查基金净值数据是否过期
        
        Args:
            fund_code: 基金代码
            max_age_hours: 最大有效期（小时）
        
        Returns:
            是否过期
        """
        from funddb import get_latest_trade_day, is_trade_day
        from datetime import date, timedelta
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 获取基金类型，判断是否为QDII基金
            cursor.execute('''
                SELECT fund_type FROM fund_info WHERE fund_code = ?
            ''', (fund_code,))
            fund_info = cursor.fetchone()
            is_qdii = fund_info and 'QDII' in (fund_info['fund_type'] or '')
            
            cursor.execute('''
                SELECT MAX(nav_date) as latest_date, MAX(update_time) as update_time
                FROM fund_nav
                WHERE fund_code = ?
            ''', (fund_code,))
            
            row = cursor.fetchone()
            if not row or not row['latest_date']:
                return True
            
            latest_date = row['latest_date']
            update_time = row['update_time']
            
            # 使用交易日历获取最近的交易日
            # 如果当前时间在下午3点之前，取昨天之前的最近交易日
            # 否则取今天之前的最近交易日
            now = datetime.now()
            if now.hour < 15:
                yesterday = date.today() - timedelta(days=1)
                expected_trade_day = get_latest_trade_day(yesterday)
            else:
                expected_trade_day = get_latest_trade_day()
            
            # QDII基金净值延迟1天，需要再往前推一个交易日
            if is_qdii:
                expected_date = datetime.strptime(expected_trade_day, '%Y-%m-%d').date()
                expected_trade_day = get_latest_trade_day(expected_date - timedelta(days=1))
            
            if latest_date < expected_trade_day:
                return True
            
            if update_time:
                update_dt = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                if datetime.now() - update_dt > timedelta(hours=max_age_hours):
                    return True
            
            return False
    
    def _get_latest_workday(self) -> str:
        """获取最近有净值数据的交易日日期（使用交易日历）"""
        from funddb import get_latest_trade_day
        
        now = datetime.now()
        if now.hour < 15:
            from datetime import date, timedelta
            yesterday = date.today() - timedelta(days=1)
            return get_latest_trade_day(yesterday)
        else:
            return get_latest_trade_day()
    
    def _check_nav_exists(self, fund_code: str) -> bool:
        """检查基金是否有净值数据"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM fund_nav WHERE fund_code = ? LIMIT 1
            ''', (fund_code,))
            return cursor.fetchone() is not None
    
    def _batch_update_nav(self, fund_codes: List[str], batch_size: int = 5):
        """批量更新基金净值"""
        for i in range(0, len(fund_codes), batch_size):
            batch = fund_codes[i:i+batch_size]
            print(f"[SmartFund] 批量更新 {i+1}-{min(i+batch_size, len(fund_codes))}/{len(fund_codes)}")
            self.skill.sync_group_nav(batch)
            time.sleep(1)
    
    def smart_batch_update_nav(self, fund_codes: List[str]) -> Dict[str, Any]:
        """
        智能批量更新净值数据（优化版）
        
        算法：
        1. 一次性查询所有基金的最新净值日期
        2. 找出目标日期（最近工作日）
        3. 只更新那些最新日期 < 目标日期的基金
        4. 已是最新日期的基金跳过，不发起API请求
        
        Args:
            fund_codes: 基金代码列表
        
        Returns:
            更新结果统计
        """
        result = {
            "total_funds": len(fund_codes),
            "funds_need_update": [],
            "funds_already_latest": [],
            "funds_no_data": [],
            "target_date": None
        }
        
        if not fund_codes:
            return result
        
        latest_workday = self._get_latest_workday()
        result["target_date"] = latest_workday
        
        fund_nav_dates = {}
        with get_db_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?' for _ in fund_codes])
            cursor.execute(f'''
                SELECT fund_code, MAX(nav_date) as latest_date
                FROM fund_nav
                WHERE fund_code IN ({placeholders})
                GROUP BY fund_code
            ''', fund_codes)
            
            for row in cursor.fetchall():
                fund_nav_dates[row['fund_code']] = row['latest_date']
        
        funds_need_update = []
        funds_already_latest = []
        funds_no_data = []
        
        for code in fund_codes:
            if code not in fund_nav_dates:
                funds_no_data.append(code)
                funds_need_update.append(code)
            elif fund_nav_dates[code] < latest_workday:
                funds_need_update.append(code)
            else:
                funds_already_latest.append(code)
        
        result["funds_need_update"] = funds_need_update
        result["funds_already_latest"] = funds_already_latest
        result["funds_no_data"] = funds_no_data
        
        print(f"[SmartFund] 智能更新分析:")
        print(f"  - 目标日期: {latest_workday}")
        print(f"  - 无数据基金: {len(funds_no_data)} 只")
        print(f"  - 需要更新: {len(funds_need_update)} 只")
        print(f"  - 已是最新: {len(funds_already_latest)} 只 (跳过API请求)")
        
        if funds_need_update:
            self._batch_update_nav(funds_need_update)
        
        return result
    
    def get_funds_nav_list_smart(self,
                                  fund_codes: List[str] = None,
                                  keyword: str = None,
                                  fund_type: str = None,
                                  company: str = None,
                                  force_update: bool = False) -> List[Dict[str, Any]]:
        """
        智能批量获取基金最新净值列表（优化版）
        
        Args:
            fund_codes: 指定基金代码列表
            keyword: 按关键词筛选
            fund_type: 按类型筛选
            company: 按公司筛选
            force_update: 是否强制更新
        
        Returns:
            基金净值列表
        """
        if not fund_codes:
            funds = self.query_funds(
                keyword=keyword,
                fund_type=fund_type,
                company=company,
                limit=100
            )
            fund_codes = [f['fund_code'] for f in funds]
        
        if not fund_codes:
            print("[SmartFund] 未找到符合条件的基金")
            return []
        
        print(f"[SmartFund] 准备获取 {len(fund_codes)} 只基金的最新净值")
        
        if force_update:
            print(f"[SmartFund] 强制更新模式")
            self._batch_update_nav(fund_codes)
        else:
            self.smart_batch_update_nav(fund_codes)
        
        result = []
        for code in fund_codes:
            nav_data = self.skill.query_fund_nav(code, limit=1)
            fund_info = self._get_fund_info(code)
            
            if nav_data and fund_info:
                result.append({
                    'fund_code': code,
                    'fund_name': fund_info['fund_name'],
                    'fund_type': fund_info['fund_type'],
                    'company_name': fund_info['company_name'],
                    'nav_date': nav_data[0]['nav_date'],
                    'unit_nav': nav_data[0]['unit_nav'],
                    'accum_nav': nav_data[0]['accum_nav'],
                    'daily_return': nav_data[0]['daily_return']
                })
        
        return result
    
    def _get_fund_info(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """获取基金基础信息"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM fund_info WHERE fund_code = ?
            ''', (fund_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== 便捷查询方法 ====================
    
    def query_funds_by_company(self, company_name: str, fund_type: str = None) -> List[Dict[str, Any]]:
        """
        按基金公司查询
        
        注意：由于数据库中company_name字段可能不完整，
        建议使用query_funds_by_keyword通过基金名称关键词查询
        
        Args:
            company_name: 公司名称关键词
            fund_type: 基金类型筛选
        
        Returns:
            基金列表
        """
        # 先尝试通过公司名查询
        results = self.query_funds(company=company_name, fund_type=fund_type, limit=200)
        
        # 如果结果太少，再通过基金名称关键词补充
        if len(results) < 10:
            keyword_results = self.query_funds(keyword=company_name, fund_type=fund_type, limit=200)
            # 合并结果，去重
            existing_codes = {r['fund_code'] for r in results}
            for fund in keyword_results:
                if fund['fund_code'] not in existing_codes:
                    results.append(fund)
        
        return results
    
    def query_funds_by_keyword(self, keyword: str, fund_type: str = None) -> List[Dict[str, Any]]:
        """
        按基金名称关键词查询（推荐）
        
        这是查询特定基金公司旗下产品的最可靠方式，
        因为基金名称中通常包含公司名称
        
        Args:
            keyword: 基金名称关键词（如'中航'、'易方达'等）
            fund_type: 基金类型筛选
        
        Returns:
            基金列表
        """
        return self.query_funds(keyword=keyword, fund_type=fund_type, limit=200)
    
    def query_by_type(self, fund_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        按基金类型查询
        
        Args:
            fund_type: 基金类型
            limit: 数量限制
        
        Returns:
            基金列表
        """
        return self.query_funds(fund_type=fund_type, limit=limit)
    
    def get_nav_summary(self, fund_codes: List[str] = None) -> Dict[str, Any]:
        """
        获取净值数据汇总统计
        
        Returns:
            统计信息
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 总基金数
            cursor.execute('SELECT COUNT(*) as count FROM fund_info')
            total_funds = cursor.fetchone()['count']
            
            # 有净值数据的基金数
            if fund_codes:
                placeholders = ','.join(['?' for _ in fund_codes])
                cursor.execute(f'''
                    SELECT COUNT(DISTINCT fund_code) as count 
                    FROM fund_nav 
                    WHERE fund_code IN ({placeholders})
                ''', fund_codes)
            else:
                cursor.execute('SELECT COUNT(DISTINCT fund_code) as count FROM fund_nav')
            
            nav_coverage = cursor.fetchone()['count']
            
            # 最新净值日期
            cursor.execute('SELECT MAX(nav_date) as latest_date FROM fund_nav')
            latest_nav_date = cursor.fetchone()['latest_date']
            
            return {
                'total_funds': total_funds,
                'nav_coverage': nav_coverage,
                'coverage_rate': f"{nav_coverage/total_funds*100:.1f}%" if total_funds > 0 else "0%",
                'latest_nav_date': latest_nav_date
            }
    
    # ==================== 风险指标和业绩数据（使用AKShare官方数据） ====================
    
    def get_fund_risk_metrics(self, fund_code: str, period: str = None) -> List[Dict[str, Any]]:
        """
        获取基金风险指标（从AKShare官方数据）
        
        数据来源：fund_individual_analysis_xq
        包含：最大回撤、夏普比率、年化波动率、同类排名等
        
        Args:
            fund_code: 基金代码
            period: 筛选特定周期（如'近1年'），None则返回所有周期
        
        Returns:
            风险指标列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if period:
                cursor.execute('''
                    SELECT * FROM fund_risk_metrics 
                    WHERE fund_code = ? AND period = ?
                ''', (fund_code, period))
            else:
                cursor.execute('''
                    SELECT * FROM fund_risk_metrics 
                    WHERE fund_code = ?
                    ORDER BY period
                ''', (fund_code,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_fund_performance(self, fund_code: str, perf_type: str = None) -> List[Dict[str, Any]]:
        """
        获取基金业绩表现（从AKShare官方数据）
        
        数据来源：fund_individual_achievement_xq
        包含：各周期收益率、年度业绩、同类排名等
        
        Args:
            fund_code: 基金代码
            perf_type: 业绩类型筛选（如'阶段业绩'、'年度业绩'）
        
        Returns:
            业绩数据列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if perf_type:
                cursor.execute('''
                    SELECT * FROM fund_performance 
                    WHERE fund_code = ? AND performance_type = ?
                    ORDER BY period
                ''', (fund_code, perf_type))
            else:
                cursor.execute('''
                    SELECT * FROM fund_performance 
                    WHERE fund_code = ?
                    ORDER BY performance_type, period
                ''', (fund_code,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_fund_period_return(self, fund_code: str, period: str = '近1年') -> Optional[float]:
        """
        获取基金特定周期收益率
        
        Args:
            fund_code: 基金代码
            period: 周期（如'近1月'、'近3月'、'近6月'、'近1年'等）
        
        Returns:
            收益率（百分比）
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT period_return FROM fund_performance 
                WHERE fund_code = ? AND performance_type = '阶段业绩' AND period = ?
            ''', (fund_code, period))
            
            row = cursor.fetchone()
            return row['period_return'] if row else None
    
    def get_fund_official_max_drawdown(self, fund_code: str, period: str = '近1年') -> Optional[float]:
        """
        获取基金官方计算的最大回撤（从AKShare）
        
        Args:
            fund_code: 基金代码
            period: 周期（如'近1年'、'近3年'、'近5年'）
        
        Returns:
            最大回撤（百分比）
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT max_drawdown FROM fund_risk_metrics 
                WHERE fund_code = ? AND period = ?
            ''', (fund_code, period))
            
            row = cursor.fetchone()
            return row['max_drawdown'] if row else None
    
    def get_funds_risk_and_return(self, 
                                   fund_codes: List[str] = None,
                                   keyword: str = None,
                                   period: str = '近1年') -> List[Dict[str, Any]]:
        """
        批量获取基金风险指标和收益率（使用AKShare官方数据）
        
        Args:
            fund_codes: 基金代码列表
            keyword: 基金名称关键词
            period: 统计周期（如'近1年'、'近3年'等）
        
        Returns:
            基金风险收益数据列表
        """
        # 如果没有提供代码，通过关键词查询
        if not fund_codes and keyword:
            funds = self.query_funds_by_keyword(keyword)
            fund_codes = [f['fund_code'] for f in funds]
        
        if not fund_codes:
            print("[SmartFund] 未找到符合条件的基金")
            return []
        
        results = []
        for code in fund_codes:
            fund_info = self._get_fund_info(code)
            if not fund_info:
                continue
            
            # 获取风险指标
            risk_data = self.get_fund_risk_metrics(code, period)
            risk_dict = risk_data[0] if risk_data else {}
            
            # 获取收益率
            period_return = self.get_fund_period_return(code, period)
            
            results.append({
                'fund_code': code,
                'fund_name': fund_info['fund_name'],
                'fund_type': fund_info['fund_type'],
                'period': period,
                'period_return': period_return,
                'max_drawdown': risk_dict.get('max_drawdown'),
                'sharpe_ratio': risk_dict.get('sharpe_ratio'),
                'annual_volatility': risk_dict.get('annual_volatility'),
                'risk_return_ratio': risk_dict.get('risk_return_ratio')
            })
        
        return results


# ==================== 便捷函数 ====================

def query_funds_nav(keyword: str = None, 
                    fund_type: str = None,
                    company: str = None,
                    force_update: bool = False) -> List[Dict[str, Any]]:
    """
    便捷函数：查询基金最新净值列表
    
    示例：
        # 查询中航基金所有权益类基金
        results = query_funds_nav(company='中航', fund_type='股票')
        
        # 查询白酒主题基金
        results = query_funds_nav(keyword='白酒')
    """
    smart = SmartFundData()
    return smart.get_funds_nav_list(
        keyword=keyword,
        fund_type=fund_type,
        company=company,
        force_update=force_update
    )


def get_fund_nav(fund_code: str, force_update: bool = False) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取单只基金最新净值
    
    示例：
        nav = get_fund_nav('000001')
    """
    smart = SmartFundData()
    return smart.get_latest_nav(fund_code, force_update)


def get_max_drawdown(fund_code: str = None,
                     keyword: str = None,
                     period: str = '近1年') -> Union[Optional[float], List[Dict[str, Any]]]:
    """
    便捷函数：获取基金最大回撤（使用AKShare官方数据）
    
    Args:
        fund_code: 单只基金代码
        keyword: 基金名称关键词（用于批量查询）
        period: 周期（如'近1年'、'近3年'、'近5年'），默认'近1年'
    
    示例：
        # 单只基金
        result = get_max_drawdown('000001', period='近1年')
        
        # 批量查询中航基金
        results = get_max_drawdown(keyword='中航', period='近1年')
    """
    smart = SmartFundData()
    
    if fund_code:
        # 单只基金
        return smart.get_fund_official_max_drawdown(fund_code, period)
    elif keyword:
        # 批量查询
        return smart.get_funds_risk_and_return(keyword=keyword, period=period)
    else:
        raise ValueError("请提供fund_code或keyword参数")


def get_fund_risk_and_return(fund_code: str = None,
                              keyword: str = None,
                              period: str = '近1年',
                              force_update: bool = False) -> Union[List[Dict], List[Dict[str, Any]]]:
    """
    便捷函数：获取基金风险指标和收益率（使用AKShare官方数据）
    
    数据来源：
    - 风险指标：fund_individual_analysis_xq（最大回撤、夏普比率、波动率等）
    - 业绩表现：fund_individual_achievement_xq（各周期收益率、同类排名等）
    
    自动刷新机制：
    - 检查数据新鲜度，超过12小时自动同步
    - 可通过 force_update=True 强制刷新
    
    Args:
        fund_code: 单只基金代码
        keyword: 基金名称关键词（用于批量查询）
        period: 统计周期（如'近1年'、'近3年'等），默认'近1年'
        force_update: 是否强制更新数据
    
    示例：
        # 单只基金完整风险指标（自动刷新）
        results = get_fund_risk_and_return('000001')
        
        # 批量查询中航基金
        results = get_fund_risk_and_return(keyword='中航', period='近1年')
        
        # 查询近3年数据
        results = get_fund_risk_and_return(keyword='中航', period='近3年')
        
        # 强制刷新数据
        results = get_fund_risk_and_return('000001', force_update=True)
    """
    smart = SmartFundData()
    
    if fund_code:
        if force_update or not _is_risk_data_fresh(fund_code):
            print(f"[SmartFund] 本地无数据或数据过期，从AKShare获取...")
            _sync_risk_and_performance(fund_code)
        else:
            print(f"[SmartFund] 使用缓存数据")
        
        return smart.get_fund_risk_metrics(fund_code)
    elif keyword:
        return smart.get_funds_risk_and_return(keyword=keyword, period=period)
    else:
        raise ValueError("请提供fund_code或keyword参数")


def calculate_value_averaging_plan(fund_code: str, 
                                    current_holding: float,
                                    simulate: bool = True) -> Dict[str, Any]:
    """
    便捷函数：计算市值定投方案
    
    核心公式：
    1. 目标市值增长额 = 当前持仓市值 × 平均月收益率
    2. 每期目标市值 = 上期目标市值 + 目标市值增长额
    3. 每期投入金额 = 目标市值 - 当前市值
    
    算法说明：
    - 基金成立≥5年：使用该基金历史数据，按当前市场阶段计算平均月收益率
    - 基金成立<5年：使用沪深300/中证500近3年平均月收益率作为参考基准
    
    Args:
        fund_code: 基金代码
        current_holding: 当前持仓市值（元）
        simulate: 是否模拟12期定投过程
    
    Returns:
        包含详细计算过程的结果字典
    
    示例：
        # 计算华夏成长混合的市值定投方案
        result = calculate_value_averaging_plan('000001', 50000)
        
        # 仅计算当期投入金额，不模拟
        result = calculate_value_averaging_plan('000001', 50000, simulate=False)
    """
    return calculate_value_averaging(fund_code, current_holding, simulate)


def get_value_averaging_report_text(fund_code: str, 
                                     current_holding: float,
                                     simulate: bool = True) -> str:
    """
    便捷函数：获取格式化的市值定投报告
    
    Args:
        fund_code: 基金代码
        current_holding: 当前持仓市值（元）
        simulate: 是否模拟12期定投过程
    
    Returns:
        格式化的报告字符串
    
    示例：
        # 获取完整报告
        report = get_value_averaging_report_text('000001', 50000)
        print(report)
    """
    return get_value_averaging_report(fund_code, current_holding, simulate)


def get_fund_holdings(fund_code: str, 
                       top_n: int = 20,
                       quarter: str = None,
                       force_update: bool = False) -> Dict[str, Any]:
    """
    便捷函数：获取基金持仓数据
    
    新鲜度判断：
    - 持仓数据一个季度更新一次，当天查询过就不再重复查询
    - 使用 fund_data_meta 表记录每只基金的持仓查询时间
    
    Args:
        fund_code: 基金代码或名称关键词
        top_n: 返回前N大持仓，默认20
        quarter: 指定季度（如'2024年4季度股票投资明细'），默认最新季度
        force_update: 是否强制更新
    
    Returns:
        包含持仓数据的字典
    """
    from funddb import update_holdings_meta
    from datetime import date
    
    smart = SmartFundData()
    
    if not fund_code.isdigit():
        funds = smart.query_funds(keyword=fund_code, limit=5)
        if funds:
            fund_code = funds[0]['fund_code']
            print(f"[SmartFund] 找到基金: {funds[0]['fund_name']} ({fund_code})")
        else:
            return {'error': f'未找到包含 "{fund_code}" 的基金'}
    
    meta_key = f'holdings_{fund_code}'
    today_str = date.today().strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查当天是否已查询过
        if not force_update:
            cursor.execute('''
                SELECT date(last_sync_time) as sync_date
                FROM fund_data_meta
                WHERE table_name = ?
            ''', (meta_key,))
            meta = cursor.fetchone()
            
            if meta and meta['sync_date'] == today_str:
                # 当天已查询过，直接返回缓存
                if quarter:
                    cursor.execute('''
                        SELECT * FROM fund_stock_holding
                        WHERE fund_code = ? AND quarter = ?
                        ORDER BY hold_ratio DESC
                        LIMIT ?
                    ''', (fund_code, quarter, top_n))
                else:
                    cursor.execute('''
                        SELECT * FROM fund_stock_holding
                        WHERE fund_code = ?
                        ORDER BY quarter DESC, hold_ratio DESC
                        LIMIT ?
                    ''', (fund_code, top_n * 5))
                
                rows = cursor.fetchall()
                
                if rows:
                    latest_quarter = rows[0]['quarter']
                    holdings = [dict(r) for r in rows if r['quarter'] == latest_quarter][:top_n]
                    print(f"[SmartFund] 使用缓存数据，报告期: {latest_quarter}")
                else:
                    holdings = []
                    latest_quarter = None
                    print(f"[SmartFund] 使用缓存数据，无持仓数据")
                
                return {
                    'fund_code': fund_code,
                    'quarter': latest_quarter,
                    'holdings': holdings,
                    'total_count': len(holdings),
                    'from_cache': True
                }
        
        # 需要从AKShare获取
        print(f"[SmartFund] 本地无数据或数据过期，从AKShare获取...")
        
        skill = FundDataSkill()
        result = skill.sync_group_holdings([fund_code])
        
        # 记录查询时间
        update_holdings_meta(fund_code, 'success' if result['success'] else 'failed')
        
        if result['success']:
            cursor.execute('''
                SELECT * FROM fund_stock_holding
                WHERE fund_code = ?
                ORDER BY quarter DESC, hold_ratio DESC
                LIMIT ?
            ''', (fund_code, top_n * 5))
            
            rows = cursor.fetchall()
            
            if rows:
                latest_quarter = rows[0]['quarter']
                holdings = [dict(r) for r in rows if r['quarter'] == latest_quarter][:top_n]
                
                return {
                    'fund_code': fund_code,
                    'quarter': latest_quarter,
                    'holdings': holdings,
                    'total_count': len(holdings),
                    'from_cache': False
                }
        
        # 没有持仓数据也返回成功，避免重复查询
        return {
            'fund_code': fund_code,
            'quarter': None,
            'holdings': [],
            'total_count': 0,
            'from_cache': False
        }


def _is_holding_data_fresh(latest_quarter: str) -> bool:
    """
    判断持仓数据是否新鲜
    
    逻辑：
    - 当前是Q1（1-3月）：最新应为去年Q4或Q3
    - 当前是Q2（4-6月）：最新应为今年Q1或去年Q4
    - 当前是Q3（7-9月）：最新应为今年Q2或Q1
    - 当前是Q4（10-12月）：最新应为今年Q3或Q2
    
    Args:
        latest_quarter: 最新季度字符串，如'2024年4季度股票投资明细'
    
    Returns:
        是否新鲜
    """
    if not latest_quarter:
        return False
    
    try:
        import re
        match = re.search(r'(\d{4})年(\d)季度', latest_quarter)
        if not match:
            return True
        
        data_year = int(match.group(1))
        data_quarter = int(match.group(2))
        
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if current_month <= 3:
            expected_quarters = [(current_year - 1, 4), (current_year - 1, 3)]
        elif current_month <= 6:
            expected_quarters = [(current_year, 1), (current_year - 1, 4)]
        elif current_month <= 9:
            expected_quarters = [(current_year, 2), (current_year, 1)]
        else:
            expected_quarters = [(current_year, 3), (current_year, 2)]
        
        data_quarter_tuple = (data_year, data_quarter)
        
        return data_quarter_tuple in expected_quarters
        
    except Exception:
        return True


def _is_risk_data_fresh(fund_code: str, max_age_hours: int = 12) -> bool:
    """
    判断风险收益数据是否新鲜
    
    逻辑：
    - 检查 fund_risk_metrics 表的 update_time
    - 检查 fund_performance 表的 update_time
    - 两个表都新鲜才返回 True
    
    Args:
        fund_code: 基金代码
        max_age_hours: 最大有效期（小时），默认12小时
    
    Returns:
        是否新鲜
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MAX(update_time) as update_time
            FROM fund_risk_metrics
            WHERE fund_code = ?
        ''', (fund_code,))
        risk_row = cursor.fetchone()
        
        cursor.execute('''
            SELECT MAX(update_time) as update_time
            FROM fund_performance
            WHERE fund_code = ?
        ''', (fund_code,))
        perf_row = cursor.fetchone()
        
        if not risk_row or not risk_row['update_time']:
            return False
        
        if not perf_row or not perf_row['update_time']:
            return False
        
        now = datetime.now()
        
        try:
            risk_update = datetime.strptime(risk_row['update_time'], '%Y-%m-%d %H:%M:%S')
            if now - risk_update > timedelta(hours=max_age_hours):
                return False
        except:
            return False
        
        try:
            perf_update = datetime.strptime(perf_row['update_time'], '%Y-%m-%d %H:%M:%S')
            if now - perf_update > timedelta(hours=max_age_hours):
                return False
        except:
            return False
        
        return True


def _sync_risk_and_performance(fund_code: str) -> bool:
    """
    同步风险指标和业绩数据
    
    Args:
        fund_code: 基金代码
    
    Returns:
        是否成功
    """
    from syncers import sync_group_risk_metrics, sync_group_performance
    
    print(f"[SmartFund] 同步 {fund_code} 的风险收益数据...")
    
    risk_result = sync_group_risk_metrics([fund_code])
    perf_result = sync_group_performance([fund_code])
    
    return risk_result.success and perf_result.success


def format_holdings_report(holdings_data: Dict[str, Any]) -> str:
    """
    便捷函数：格式化持仓报告
    
    Args:
        holdings_data: get_fund_holdings返回的数据
    
    Returns:
        格式化的报告字符串
    """
    if 'error' in holdings_data:
        return f"错误: {holdings_data['error']}"
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"基金持仓报告: {holdings_data['fund_code']}")
    lines.append("=" * 70)
    lines.append(f"报告期: {holdings_data['quarter']}")
    lines.append(f"持仓股票数: {holdings_data['total_count']}")
    cache_status = "(缓存)" if holdings_data.get('from_cache', False) else "(新获取)"
    lines.append(f"数据来源: {cache_status}")
    lines.append("")
    lines.append(f"{'股票代码':<10} {'股票名称':<12} {'占净值比例':>10} {'持仓市值':>15}")
    lines.append("-" * 50)
    
    for h in holdings_data['holdings']:
        lines.append(f"{h['stock_code']:<10} {h['stock_name']:<12} {h['hold_ratio']:>10.2f}% {h['hold_value']:>15,.0f}")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def get_portfolio_funds_full(portfolio_id: int = None,
                              portfolio_name: str = None,
                              force_update: bool = False) -> Dict[str, Any]:
    """
    聚合查询：获取组合内所有基金的完整信息

    自动刷新机制：
    - 净值数据：自动检查并刷新（24小时有效期）
    - 持仓数据：自动检查并刷新（按季度）
    - 风险收益指标：自动检查并刷新（12小时有效期，基于metrics_update_time）

    实时计算指标（不存储在数据库）：
    - 可用现金：根据交易记录实时计算（卖出所得 - 买入投入）
    - 市值：shares × unit_nav
    - 成本：shares × buy_nav
    - 盈亏：(unit_nav - buy_nav) × shares

    Args:
        portfolio_id: 组合ID
        portfolio_name: 组合名称（与ID二选一）
        force_update: 是否强制更新所有数据

    Returns:
        包含组合完整信息的字典

    示例：
        # 按ID查询
        result = get_portfolio_funds_full(portfolio_id=2)

        # 按名称查询
        result = get_portfolio_funds_full(portfolio_name='持仓组合')

        # 强制刷新
        result = get_portfolio_funds_full(portfolio_id=2, force_update=True)
    """
    from portfolio_manager import list_portfolios, list_portfolio_funds, PortfolioManager, calculate_fund_available_cash

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
        if not portfolio_id:
            return {'error': f'未找到组合: {portfolio_name}'}

    funds = list_portfolio_funds(portfolio_id)
    if not funds:
        return {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio_name,
            'fund_count': 0,
            'funds': []
        }

    smart = SmartFundData()
    pm = PortfolioManager()
    result_funds = []

    # 统计信息
    freshness_summary = {
        'nav_fresh_count': 0,
        'metrics_fresh_count': 0,
        'metrics_updated_count': 0,
        'total_funds': len(funds)
    }

    for fund in funds:
        fund_code = fund['fund_code']
        fund_info = {
            'fund_code': fund_code,
            'fund_name': fund.get('fund_name', ''),
            'buy_date': fund.get('buy_date'),
            'buy_nav': fund.get('buy_nav'),
            'shares': fund.get('shares'),
            'amount': fund.get('amount'),
            'notes': fund.get('notes'),
        }

        basic_info = smart._get_fund_info(fund_code)
        if basic_info:
            fund_info['fund_type'] = basic_info.get('fund_type')
            fund_info['company_name'] = basic_info.get('company_name')

        # 获取净值（自动检查新鲜度）
        nav = get_fund_nav(fund_code, force_update=force_update)
        if nav:
            fund_info['unit_nav'] = nav.get('unit_nav')
            fund_info['nav_date'] = nav.get('nav_date')
            fund_info['daily_return'] = nav.get('daily_return')
            freshness_summary['nav_fresh_count'] += 1

        # 检查并刷新风险收益指标（基于metrics_update_time）
        metrics_update_time = fund.get('metrics_update_time')
        need_update_metrics = force_update

        if not force_update and metrics_update_time:
            try:
                last_update = datetime.strptime(metrics_update_time, '%Y-%m-%d %H:%M:%S')
                if datetime.now() - last_update > timedelta(hours=12):
                    need_update_metrics = True
            except:
                need_update_metrics = True
        elif not metrics_update_time:
            need_update_metrics = True

        if need_update_metrics:
            # 刷新指标
            refresh_result = pm.refresh_portfolio_fund_metrics(portfolio_id, fund_code)
            if refresh_result.get('success'):
                freshness_summary['metrics_updated_count'] += 1
                # 重新获取基金数据
                refreshed_funds = pm.list_portfolio_funds(portfolio_id)
                for rf in refreshed_funds:
                    if rf['fund_code'] == fund_code:
                        fund = rf
                        break
        else:
            freshness_summary['metrics_fresh_count'] += 1

        # 从portfolio_fund表读取指标字段
        fund_info['return_1m'] = fund.get('return_1m')
        fund_info['return_6m'] = fund.get('return_6m')
        fund_info['return_1y'] = fund.get('return_1y')
        fund_info['max_drawdown_1y'] = fund.get('max_drawdown_1y')
        fund_info['sharpe_ratio_1y'] = fund.get('sharpe_ratio_1y')
        fund_info['annual_volatility_1y'] = fund.get('annual_volatility_1y')
        fund_info['rank_in_category'] = fund.get('rank_in_category')
        fund_info['rank_category'] = fund.get('rank_category')
        fund_info['metrics_update_time'] = fund.get('metrics_update_time')

        # 获取持仓数据
        holdings = get_fund_holdings(fund_code, top_n=5, force_update=force_update)
        if 'error' not in holdings:
            fund_info['top_holdings'] = holdings.get('holdings', [])
            fund_info['holdings_quarter'] = holdings.get('quarter')

        # 计算可用现金（实时计算，不存储在数据库）
        cash_info = calculate_fund_available_cash(portfolio_id, fund_code)
        if cash_info['success']:
            fund_info['available_cash'] = cash_info['available_cash']
            fund_info['total_buy_amount'] = cash_info['total_buy_amount']
            fund_info['total_sell_amount'] = cash_info['total_sell_amount']

        result_funds.append(fund_info)

    return {
        'portfolio_id': portfolio_id,
        'portfolio_name': portfolio_name,
        'fund_count': len(result_funds),
        'freshness_summary': freshness_summary,
        'funds': result_funds
    }


def format_portfolio_report(portfolio_data: Dict[str, Any]) -> str:
    """
    格式化组合报告
    
    Args:
        portfolio_data: get_portfolio_funds_full返回的数据
    
    Returns:
        格式化的报告字符串
    """
    if 'error' in portfolio_data:
        return f"错误: {portfolio_data['error']}"
    
    lines = []
    lines.append("=" * 100)
    lines.append(f"组合报告: {portfolio_data['portfolio_name']} (ID: {portfolio_data['portfolio_id']})")
    lines.append(f"基金数量: {portfolio_data['fund_count']}")
    lines.append("=" * 100)
    
    for i, fund in enumerate(portfolio_data['funds'], 1):
        lines.append(f"\n[{i}] {fund['fund_code']} {fund['fund_name']}")
        
        if fund.get('fund_type'):
            lines.append(f"    类型: {fund['fund_type']}  公司: {fund.get('company_name', '-')}")
        
        if fund.get('unit_nav'):
            daily_ret = fund.get('daily_return')
            daily_ret_str = f"{daily_ret:.2f}%" if daily_ret is not None else "-"
            lines.append(f"    净值: {fund['unit_nav']} ({fund['nav_date']})  日涨跌: {daily_ret_str}")
        
        ret_1m = fund.get('return_1m')
        ret_6m = fund.get('return_6m')
        ret_1y = fund.get('return_1y')
        ret_1m_str = f"{ret_1m:.4f}%" if ret_1m is not None else "-"
        ret_6m_str = f"{ret_6m:.4f}%" if ret_6m is not None else "-"
        ret_1y_str = f"{ret_1y:.4f}%" if ret_1y is not None else "-"
        lines.append(f"    收益率: 近1月 {ret_1m_str} | 近6月 {ret_6m_str} | 近1年 {ret_1y_str}")
        
        max_dd = fund.get('max_drawdown_1y')
        sharpe = fund.get('sharpe_ratio_1y')
        volatility = fund.get('annual_volatility_1y')
        period_ret = fund.get('period_return_1y')
        max_dd_str = f"{max_dd:.2f}%" if max_dd is not None else "-"
        sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "-"
        volatility_str = f"{volatility:.2f}%" if volatility is not None else "-"
        period_ret_str = f"{period_ret:.2f}%" if period_ret is not None else "-"
        lines.append(f"    风险(近1年): 回撤 {max_dd_str} | 波动率 {volatility_str} | 夏普 {sharpe_str} | 收益率 {period_ret_str}")
        
        max_dd_since = fund.get('max_drawdown_since')
        ret_since = fund.get('return_since')
        if max_dd_since is not None or ret_since is not None:
            dd_since_str = f"{max_dd_since:.2f}%" if max_dd_since is not None else "-"
            ret_since_str = f"{ret_since:.2f}%" if ret_since is not None else "-"
            lines.append(f"    风险(成立以来): 回撤 {dd_since_str} | 收益率 {ret_since_str}")
        
        rank = fund.get('rank_in_category')
        category = fund.get('rank_category')
        if rank is not None or category:
            rank_str = f"第{rank}名" if rank is not None else "-"
            category_str = category if category else "-"
            lines.append(f"    同类排名: {rank_str} ({category_str})")
        
        if fund.get('buy_date') or fund.get('shares') or fund.get('amount'):
            holding_parts = []
            if fund.get('buy_date'):
                holding_parts.append(f"买入日期: {fund['buy_date']}")
            if fund.get('buy_nav'):
                holding_parts.append(f"买入净值: {fund['buy_nav']}")
            if fund.get('shares'):
                holding_parts.append(f"份额: {fund['shares']}")
            if fund.get('amount'):
                holding_parts.append(f"金额: {fund['amount']}")
            lines.append(f"    持仓信息: {' | '.join(holding_parts)}")

        # 显示可用现金（实时计算）
        available_cash = fund.get('available_cash')
        if available_cash is not None:
            cash_str = f"{available_cash:,.2f}" if available_cash != 0 else "0.00"
            if available_cash > 0:
                lines.append(f"    可用现金: {cash_str} (净卖出)")
            elif available_cash < 0:
                lines.append(f"    可用现金: {cash_str} (净投入)")
            else:
                lines.append(f"    可用现金: {cash_str}")

        if fund.get('notes'):
            lines.append(f"    备注: {fund['notes']}")
        
        if fund.get('top_holdings'):
            lines.append(f"    前5大持仓 ({fund.get('holdings_quarter', '')}):")
            for h in fund['top_holdings'][:5]:
                hold_ratio = h.get('hold_ratio')
                hold_ratio_str = f"{hold_ratio:.2f}%" if hold_ratio is not None else "-"
                lines.append(f"      {h['stock_code']} {h['stock_name']}: {hold_ratio_str}")
    
    lines.append("\n" + "=" * 100)
    
    return "\n".join(lines)


# ==================== 止盈相关便捷函数 ====================

def get_take_profit_advice(portfolio_id: int) -> Dict[str, Any]:
    """
    便捷函数：获取组合止盈建议
    
    自动获取各基金配置的参数，计算止盈建议
    
    Args:
        portfolio_id: 组合ID
    
    Returns:
        止盈建议数据
    
    示例：
        result = get_take_profit_advice(portfolio_id=1)
    """
    from take_profit import calculate_portfolio_take_profit
    return calculate_portfolio_take_profit(portfolio_id)


def get_take_profit_report(portfolio_id: int) -> str:
    """
    便捷函数：获取格式化的止盈报告
    
    Args:
        portfolio_id: 组合ID
    
    Returns:
        格式化的报告字符串
    
    示例：
        report = get_take_profit_report(portfolio_id=1)
        print(report)
    """
    from take_profit import get_take_profit_report_text
    return get_take_profit_report_text(portfolio_id)


def list_take_profit_templates() -> List[Dict[str, Any]]:
    """
    便捷函数：获取所有止盈参数模板
    
    Returns:
        模板列表
    
    示例：
        templates = list_take_profit_templates()
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().list_templates()


def get_take_profit_template(template_id: int) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取单个止盈参数模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        模板详情
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().get_template(template_id)


def get_default_take_profit_template() -> Dict[str, Any]:
    """
    便捷函数：获取默认止盈参数模板
    
    Returns:
        默认模板
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().get_default_template()


def create_take_profit_template(name: str, description: str = None, **params) -> Dict[str, Any]:
    """
    便捷函数：创建止盈参数模板
    
    Args:
        name: 模板名称
        description: 模板描述
        **params: 止盈参数
    
    Returns:
        创建结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().create_template(name=name, description=description, **params)


def update_take_profit_template(template_id: int, **kwargs) -> Dict[str, Any]:
    """
    便捷函数：更新止盈参数模板
    
    Args:
        template_id: 模板ID
        **kwargs: 可更新字段
    
    Returns:
        更新结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().update_template(template_id, **kwargs)


def delete_take_profit_template(template_id: int) -> Dict[str, Any]:
    """
    便捷函数：删除止盈参数模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        删除结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().delete_template(template_id)


def set_default_take_profit_template(template_id: int) -> Dict[str, Any]:
    """
    便捷函数：设置默认止盈参数模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        设置结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().set_default_template(template_id)


def get_fund_take_profit_config(portfolio_id: int, fund_code: str) -> Dict[str, Any]:
    """
    便捷函数：获取基金的止盈配置
    
    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
    
    Returns:
        基金止盈配置（合并模板参数后的最终参数）
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().get_fund_config(portfolio_id, fund_code)


def set_fund_take_profit_template(portfolio_id: int, fund_code: str, template_id: int = None) -> Dict[str, Any]:
    """
    便捷函数：为基金设置止盈参数模板
    
    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        template_id: 模板ID（None表示使用默认模板）
    
    Returns:
        设置结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().set_fund_template(portfolio_id, fund_code, template_id)


def set_fund_take_profit_custom_params(portfolio_id: int, fund_code: str, **kwargs) -> Dict[str, Any]:
    """
    便捷函数：为基金设置自定义止盈参数
    
    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        **kwargs: 自定义参数
    
    Returns:
        设置结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().set_fund_custom_params(portfolio_id, fund_code, **kwargs)


def reset_fund_take_profit_config(portfolio_id: int, fund_code: str) -> Dict[str, Any]:
    """
    便捷函数：重置基金止盈配置为默认
    
    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
    
    Returns:
        重置结果
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().reset_fund_config(portfolio_id, fund_code)


def get_portfolio_take_profit_configs(portfolio_id: int) -> List[Dict[str, Any]]:
    """
    便捷函数：获取组合内所有基金的止盈配置

    Args:
        portfolio_id: 组合ID

    Returns:
        所有基金的配置列表
    """
    from take_profit_manager import TakeProfitTemplateManager
    return TakeProfitTemplateManager().get_portfolio_fund_configs(portfolio_id)


def execute_buy_back_transaction(portfolio_id: int, fund_code: str,
                                 target_sell_transaction_id: int,
                                 shares: float, amount: float,
                                 transaction_date: str = None,
                                 nav: float = None, fee: float = 0,
                                 notes: str = None) -> Dict[str, Any]:
    """
    便捷函数：执行波段捡回交易

    功能：
    1. 记录买入交易
    2. 标记对应的卖出记录为已回收 (is_recovered = 1)
    3. 扣除组合现金

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        target_sell_transaction_id: 目标卖出交易记录ID（要标记为已回收的卖单）
        shares: 买入份额
        amount: 买入金额
        transaction_date: 交易日期（默认今天）
        nav: 交易时净值（可选）
        fee: 手续费（可选）
        notes: 备注（可选）

    Returns:
        交易记录结果

    Example:
        >>> result = execute_buy_back_transaction(
        ...     portfolio_id=1,
        ...     fund_code='000001',
        ...     target_sell_transaction_id=123,
        ...     shares=1000,
        ...     amount=1200.00,
        ...     nav=1.20
        ... )
        >>> print(result)
        {
            'success': True,
            'transaction_type': 'BUY',
            'fund_code': '000001',
            'fund_name': '华夏成长',
            'shares': 1000,
            'amount': 1200.00,
            'target_sell_transaction_id': 123,
            'buy_transaction_id': 456,
            'new_cash_balance': 8800.00,
            'transaction_date': '2025-02-18'
        }
    """
    from portfolio_manager import execute_buy_back_transaction as _execute_buy_back
    return _execute_buy_back(
        portfolio_id=portfolio_id,
        fund_code=fund_code,
        target_sell_transaction_id=target_sell_transaction_id,
        shares=shares,
        amount=amount,
        transaction_date=transaction_date,
        nav=nav,
        fee=fee,
        notes=notes
    )


if __name__ == '__main__':
    # 测试
    smart = SmartFundData()
    
    print("=" * 80)
    print("SmartFundData 智能基金数据管理测试")
    print("=" * 80)
    
    # 测试1: 通用查询
    print("\n1. 查询中航基金权益类基金:")
    results = smart.query_funds(company='中航', fund_type='股票', limit=5)
    for r in results:
        print(f"  {r['fund_code']} - {r['fund_name']}")
    
    # 测试2: 获取最新净值（智能缓存）
    print("\n2. 获取单只基金最新净值（首次，需要更新）:")
    nav = smart.get_latest_nav('000001')
    if nav:
        print(f"  000001 最新净值: {nav['unit_nav']} ({nav['nav_date']})")
    
    print("\n3. 再次获取（应该使用缓存）:")
    nav = smart.get_latest_nav('000001')
    if nav:
        print(f"  000001 最新净值: {nav['unit_nav']} ({nav['nav_date']})")
    
    # 测试3: 批量获取
    print("\n4. 批量获取中航基金净值:")
    nav_list = smart.get_funds_nav_list(company='中航', fund_type='混合', limit=3)
    for item in nav_list:
        print(f"  {item['fund_code']} - {item['fund_name']}: {item.get('unit_nav', 'N/A')}")
