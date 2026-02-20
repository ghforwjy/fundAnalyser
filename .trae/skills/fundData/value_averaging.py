"""
市值定投法（Value Averaging Strategy）模块

核心公式（修正版）：
1. 基准市值 = 基准日期持仓份额 × 基准日期净值
2. 目标增长额 = 基准市值 × 平均月收益率 × (天数/30)
3. 目标市值 = 基准市值 + 目标增长额
4. 投入金额 = 目标市值 - 当前实际市值

算法说明：
- 使用历史持仓份额作为基准，而非当前持仓份额
- 支持任意日期回溯，不仅限于按月计算
- 区分"原有持仓的盈亏"和"新买入的本金"
- 基金成立≥5年：使用该基金历史数据，按当前市场阶段计算平均月收益率
- 基金成立<5年：使用沪深300/中证500在当前市场阶段的平均月收益率作为参考基准

新鲜度算法：
- 指数参考基准有效期：1年
- 每次计算前先确认当前市场阶段
- 如果市场阶段变化，重新计算参考基准
- 如果市场阶段未变化且数据在有效期内，使用缓存数据
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from funddb import get_db_connection


MARKET_PHASES = {
    "牛市尾声": ("2021-01", "2021-02"),
    "熊市": ("2021-03", "2023-12"),
    "牛市": ("2024-01", "2025-12")
}

CURRENT_PHASE = "牛市"

BENCHMARK_VALIDITY_DAYS = 365


class ValueAveragingCalculator:
    """
    市值定投计算器
    
    提供目标市值增长额计算、定投模拟等功能
    """
    
    # 类级别缓存：基金平均月收益率
    _fund_return_cache = {}
    
    def __init__(self):
        self.hs300_code = "510300"
        self.zz500_code = "510500"
        self._init_market_phase()
    
    def _get_cached_fund_return(self, fund_code: str, market_phase: str) -> tuple:
        """
        获取缓存的基金平均月收益率
        
        Returns:
            (avg_return, is_fresh): 平均月收益率和是否新鲜
        """
        cache_key = f"{fund_code}_{market_phase}"
        if cache_key in self._fund_return_cache:
            cached = self._fund_return_cache[cache_key]
            # 缓存有效期：30天
            days_since_cache = (datetime.now() - cached['cache_time']).days
            if days_since_cache <= 30:
                return cached['avg_return'], True
        return None, False
    
    def _cache_fund_return(self, fund_code: str, market_phase: str, avg_return: float):
        """缓存基金平均月收益率"""
        cache_key = f"{fund_code}_{market_phase}"
        self._fund_return_cache[cache_key] = {
            'avg_return': avg_return,
            'cache_time': datetime.now()
        }
    
    def _init_market_phase(self):
        """初始化市场阶段"""
        current_phase = self._get_current_market_phase()
        if current_phase:
            global CURRENT_PHASE
            CURRENT_PHASE = current_phase
    
    def _get_current_market_phase(self) -> str:
        """从数据库获取当前市场阶段"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT phase_name FROM market_phase_record
                    WHERE is_current = 1
                    ORDER BY update_time DESC
                    LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    return row['phase_name']
        except:
            pass
        return CURRENT_PHASE
    
    def _save_market_phase(self, phase_name: str, start_date: str, end_date: str = None):
        """保存市场阶段到数据库"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE market_phase_record SET is_current = 0')
                cursor.execute('''
                    INSERT OR REPLACE INTO market_phase_record
                    (phase_name, start_date, end_date, is_current, confirmed_date, update_time)
                    VALUES (?, ?, ?, 1, date('now'), datetime('now'))
                ''', (phase_name, start_date, end_date))
                conn.commit()
        except Exception as e:
            print(f"[ValueAveraging] 保存市场阶段失败: {e}")
    
    def _get_cached_benchmark(self, index_code: str, market_phase: str) -> dict:
        """获取缓存的指数参考基准"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT avg_monthly_return, monthly_return_std, sample_months,
                           update_time, data_start_date, data_end_date
                    FROM index_benchmark
                    WHERE index_code = ? AND market_phase = ?
                ''', (index_code, market_phase))
                
                row = cursor.fetchone()
                if row:
                    update_time = datetime.strptime(row['update_time'], '%Y-%m-%d %H:%M:%S')
                    days_since_update = (datetime.now() - update_time).days
                    
                    return {
                        'avg_monthly_return': row['avg_monthly_return'],
                        'monthly_return_std': row['monthly_return_std'],
                        'sample_months': row['sample_months'],
                        'data_start_date': row['data_start_date'],
                        'data_end_date': row['data_end_date'],
                        'is_fresh': days_since_update <= BENCHMARK_VALIDITY_DAYS,
                        'days_since_update': days_since_update
                    }
        except Exception as e:
            print(f"[ValueAveraging] 获取缓存基准失败: {e}")
        
        return {'is_fresh': False}
    
    def _save_benchmark(self, index_code: str, index_name: str, market_phase: str,
                        avg_return: float, std_return: float, sample_months: int,
                        start_date: str, end_date: str):
        """保存指数参考基准到数据库"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO index_benchmark
                    (index_code, index_name, market_phase, avg_monthly_return, 
                     monthly_return_std, sample_months, data_start_date, data_end_date, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (index_code, index_name, market_phase, avg_return, 
                      std_return, sample_months, start_date, end_date))
                conn.commit()
        except Exception as e:
            print(f"[ValueAveraging] 保存基准失败: {e}")
    
    def _check_market_phase_changed(self) -> bool:
        """检查市场阶段是否发生变化"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT phase_name, update_time FROM market_phase_record
                    WHERE is_current = 1
                    ORDER BY update_time DESC
                    LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    return row['phase_name'] != CURRENT_PHASE
        except:
            pass
        return True
    
    def get_fund_info(self, fund_code: str) -> dict:
        """
        获取基金基本信息，包括成立日期（从本地数据库查询）
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT fund_code, fund_name, fund_type, establish_date, company_name
                    FROM fund_info
                    WHERE fund_code = ?
                ''', (fund_code,))
                row = cursor.fetchone()
                if row:
                    info = {
                        '基金全称': row['fund_name'],
                        '基金简称': row['fund_name'],
                        '基金类型': row['fund_type'] or '未知',
                        '成立日期': row['establish_date'],
                        '基金公司': row['company_name'],
                    }
                    return info
            return {}
        except Exception as e:
            print(f"[ValueAveraging] 获取基金信息失败: {e}")
            return {}
    
    def get_fund_nav_history(self, fund_code: str, years: int = 5) -> pd.DataFrame:
        """
        获取基金历史净值数据（智能缓存：先检查新鲜度，必要时更新）
        """
        try:
            # 先检查净值数据新鲜度，如过期则更新
            if self._is_nav_stale(fund_code):
                print(f"[ValueAveraging] 基金 {fund_code} 净值数据过期，正在更新...")
                from fund_data_skill import FundDataSkill
                skill = FundDataSkill()
                skill.sync_group_nav([fund_code])
            
            with get_db_connection() as conn:
                # 计算起始日期
                start_date = (datetime.now() - timedelta(days=years * 365)).strftime('%Y-%m-%d')

                cursor = conn.cursor()
                cursor.execute('''
                    SELECT nav_date as 净值日期, unit_nav as 单位净值
                    FROM fund_nav
                    WHERE fund_code = ? AND nav_date >= ?
                    ORDER BY nav_date
                ''', (fund_code, start_date))
                rows = cursor.fetchall()

                if rows:
                    df = pd.DataFrame(rows, columns=['净值日期', '单位净值'])
                    df['净值日期'] = pd.to_datetime(df['净值日期'])
                    return df
                return None
        except Exception as e:
            print(f"[ValueAveraging] 获取基金净值失败: {e}")
            return None
    
    def _is_nav_stale(self, fund_code: str, max_age_hours: int = 24) -> bool:
        """
        检查基金净值数据是否过期
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
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
                
                latest_workday = self._get_latest_workday()
                
                if latest_date < latest_workday:
                    return True
                
                if update_time:
                    update_dt = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                    if datetime.now() - update_dt > timedelta(hours=max_age_hours):
                        return True
                
                return False
        except Exception as e:
            print(f"[ValueAveraging] 检查净值新鲜度失败: {e}")
            return True
    
    def _get_latest_workday(self) -> str:
        """获取最近工作日日期"""
        today = datetime.now()
        weekday = today.weekday()
        
        if weekday == 5:  # 周六
            latest = today - timedelta(days=1)
        elif weekday == 6:  # 周日
            latest = today - timedelta(days=2)
        else:
            latest = today
        
        return latest.strftime('%Y-%m-%d')
    
    def get_etf_history(self, etf_code: str, years: int = 3) -> pd.DataFrame:
        """
        获取ETF历史行情数据
        """
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y%m%d")
            
            df = ak.fund_etf_hist_em(
                symbol=etf_code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust="hfq"
            )
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            return df
        except Exception as e:
            print(f"[ValueAveraging] 获取ETF数据失败: {e}")
            return None
    
    def calculate_monthly_returns_from_nav(self, df: pd.DataFrame, date_col: str = "净值日期", nav_col: str = "单位净值") -> pd.DataFrame:
        """
        从净值数据计算月度收益率
        """
        df = df.copy()
        df['月份'] = df[date_col].dt.to_period('M')
        
        monthly_df = df.groupby('月份').agg({
            nav_col: ['first', 'last']
        }).reset_index()
        
        monthly_df.columns = ['月份', '月初净值', '月末净值']
        monthly_df['月收益率'] = (monthly_df['月末净值'] / monthly_df['月初净值'] - 1) * 100
        
        return monthly_df
    
    def calculate_monthly_returns_from_price(self, df: pd.DataFrame, date_col: str = "日期", price_col: str = "收盘") -> pd.DataFrame:
        """
        从价格数据计算月度收益率
        """
        df = df.copy()
        df['月份'] = df[date_col].dt.to_period('M')
        
        monthly_df = df.groupby('月份').agg({
            price_col: ['first', 'last']
        }).reset_index()
        
        monthly_df.columns = ['月份', '月初价格', '月末价格']
        monthly_df['月收益率'] = (monthly_df['月末价格'] / monthly_df['月初价格'] - 1) * 100
        
        return monthly_df
    
    def analyze_by_market_phase(self, monthly_df: pd.DataFrame) -> dict:
        """
        按牛熊市阶段分析收益率
        """
        results = {}
        
        for phase_name, (start, end) in MARKET_PHASES.items():
            phase_df = monthly_df[
                (monthly_df['月份'] >= start) & 
                (monthly_df['月份'] <= end)
            ]
            
            if len(phase_df) > 0:
                avg_return = phase_df['月收益率'].mean()
                std_return = phase_df['月收益率'].std()
                count = len(phase_df)
                
                results[phase_name] = {
                    "月数": count,
                    "平均月收益率": avg_return,
                    "月收益率标准差": std_return
                }
        
        return results
    
    def calculate_target_growth(self, fund_code: str, current_holding: float) -> dict:
        """
        计算目标市值增长额
        
        Args:
            fund_code: 基金代码
            current_holding: 当前持仓市值
        
        Returns:
            包含详细计算过程的结果字典
        """
        result = {
            "fund_code": fund_code,
            "current_holding": current_holding,
            "calculation_method": "",
            "reference_source": "",
            "market_phase": CURRENT_PHASE,
            "avg_monthly_return": 0,
            "target_growth": 0,
            "algorithm_details": []
        }
        
        fund_info = self.get_fund_info(fund_code)
        
        establish_date = None
        if '成立日期' in fund_info:
            try:
                establish_date = pd.to_datetime(fund_info['成立日期'])
            except:
                pass
        
        today = datetime.now()
        fund_age_years = 0
        if establish_date:
            fund_age_years = (today - establish_date).days / 365
        
        result["fund_name"] = fund_info.get('基金简称', '未知')
        result["fund_type"] = fund_info.get('基金类型', '未知')
        result["fund_age_years"] = fund_age_years
        result["establish_date"] = fund_info.get('成立日期', '未知')
        
        if fund_age_years >= 5:
            result["calculation_method"] = "基金自身历史数据"
            result["reference_source"] = f"基金{fund_code}历史净值（近5年）"
            
            nav_df = self.get_fund_nav_history(fund_code, years=5)
            if nav_df is None or len(nav_df) == 0:
                result["error"] = "无法获取基金净值数据"
                return result
            
            monthly_df = self.calculate_monthly_returns_from_nav(nav_df)
            market_phases = self.analyze_by_market_phase(monthly_df)
            
            result["market_phases"] = market_phases
            
            if CURRENT_PHASE in market_phases:
                avg_monthly_return = market_phases[CURRENT_PHASE]['平均月收益率']
                result["algorithm_details"].append(f"当前市场阶段: {CURRENT_PHASE}")
                result["algorithm_details"].append(f"该阶段历史平均月收益率: {avg_monthly_return:.2f}%")
                result["algorithm_details"].append(f"该阶段历史月收益率标准差: {market_phases[CURRENT_PHASE]['月收益率标准差']:.2f}%")
            else:
                avg_monthly_return = monthly_df['月收益率'].mean()
                result["algorithm_details"].append(f"使用全部历史平均月收益率: {avg_monthly_return:.2f}%")
            
            result["avg_monthly_return"] = avg_monthly_return
            
        else:
            result["calculation_method"] = "指数参考基准（按市场阶段）"
            result["algorithm_details"].append(f"基金成立年限({fund_age_years:.1f}年)不足5年，使用沪深300/中证500作为参考基准")
            result["algorithm_details"].append(f"当前市场阶段: {CURRENT_PHASE}")
            
            phase_changed = self._check_market_phase_changed()
            
            hs300_cached = self._get_cached_benchmark(self.hs300_code, CURRENT_PHASE)
            zz500_cached = self._get_cached_benchmark(self.zz500_code, CURRENT_PHASE)
            
            use_cache = (not phase_changed and 
                        hs300_cached.get('is_fresh', False) and 
                        zz500_cached.get('is_fresh', False))
            
            if use_cache:
                result["algorithm_details"].append(f"使用缓存数据（有效期1年）")
                hs300_phase_return = hs300_cached['avg_monthly_return']
                zz500_phase_return = zz500_cached['avg_monthly_return']
                
                result["algorithm_details"].append(f"沪深300ETF在{CURRENT_PHASE}阶段平均月收益率: {hs300_phase_return:.2f}% (缓存)")
                result["algorithm_details"].append(f"中证500ETF在{CURRENT_PHASE}阶段平均月收益率: {zz500_phase_return:.2f}% (缓存)")
                
                avg_monthly_return = (hs300_phase_return + zz500_phase_return) / 2
                result["reference_source"] = f"沪深300ETF在{CURRENT_PHASE}阶段月收益率 {hs300_phase_return:.2f}% + 中证500ETF在{CURRENT_PHASE}阶段月收益率 {zz500_phase_return:.2f}% (缓存)"
                result["from_cache"] = True
            else:
                result["algorithm_details"].append(f"重新计算参考基准（市场阶段变化或数据过期）")
                
                hs300_df = self.get_etf_history(self.hs300_code, years=5)
                zz500_df = self.get_etf_history(self.zz500_code, years=5)
                
                hs300_monthly = self.calculate_monthly_returns_from_price(hs300_df)
                zz500_monthly = self.calculate_monthly_returns_from_price(zz500_df)
                
                hs300_phases = self.analyze_by_market_phase(hs300_monthly)
                zz500_phases = self.analyze_by_market_phase(zz500_monthly)
                
                result["hs300_phases"] = hs300_phases
                result["zz500_phases"] = zz500_phases
                
                if CURRENT_PHASE in hs300_phases and CURRENT_PHASE in zz500_phases:
                    hs300_phase_return = hs300_phases[CURRENT_PHASE]['平均月收益率']
                    hs300_phase_std = hs300_phases[CURRENT_PHASE]['月收益率标准差']
                    hs300_months = hs300_phases[CURRENT_PHASE]['月数']
                    
                    zz500_phase_return = zz500_phases[CURRENT_PHASE]['平均月收益率']
                    zz500_phase_std = zz500_phases[CURRENT_PHASE]['月收益率标准差']
                    zz500_months = zz500_phases[CURRENT_PHASE]['月数']
                    
                    phase_dates = MARKET_PHASES.get(CURRENT_PHASE, ("", ""))
                    
                    self._save_benchmark(
                        self.hs300_code, "沪深300ETF", CURRENT_PHASE,
                        hs300_phase_return, hs300_phase_std, hs300_months,
                        phase_dates[0], phase_dates[1]
                    )
                    self._save_benchmark(
                        self.zz500_code, "中证500ETF", CURRENT_PHASE,
                        zz500_phase_return, zz500_phase_std, zz500_months,
                        phase_dates[0], phase_dates[1]
                    )
                    
                    self._save_market_phase(CURRENT_PHASE, phase_dates[0], phase_dates[1])
                    
                    result["algorithm_details"].append(f"沪深300ETF在{CURRENT_PHASE}阶段平均月收益率: {hs300_phase_return:.2f}%")
                    result["algorithm_details"].append(f"中证500ETF在{CURRENT_PHASE}阶段平均月收益率: {zz500_phase_return:.2f}%")
                    
                    avg_monthly_return = (hs300_phase_return + zz500_phase_return) / 2
                    result["reference_source"] = f"沪深300ETF在{CURRENT_PHASE}阶段月收益率 {hs300_phase_return:.2f}% + 中证500ETF在{CURRENT_PHASE}阶段月收益率 {zz500_phase_return:.2f}%"
                else:
                    hs300_avg = hs300_monthly['月收益率'].mean()
                    zz500_avg = zz500_monthly['月收益率'].mean()
                    avg_monthly_return = (hs300_avg + zz500_avg) / 2
                    result["reference_source"] = f"沪深300ETF近5年平均月收益率 {hs300_avg:.2f}% + 中证500ETF近5年平均月收益率 {zz500_avg:.2f}%"
                    result["algorithm_details"].append(f"未找到{CURRENT_PHASE}阶段数据，使用近5年平均值")
                
                result["from_cache"] = False
            
            result["algorithm_details"].append(f"综合参考基准(两者平均): {avg_monthly_return:.2f}%")
            
            result["avg_monthly_return"] = avg_monthly_return
        
        target_growth = current_holding * avg_monthly_return / 100
        result["target_growth"] = target_growth
        
        result["algorithm_details"].append(f"")
        result["algorithm_details"].append(f"【计算公式】")
        result["algorithm_details"].append(f"目标市值增长额 = 当前持仓市值 × 平均月收益率")
        result["algorithm_details"].append(f"            = {current_holding:,.0f} × {avg_monthly_return:.2f}%")
        result["algorithm_details"].append(f"            = {target_growth:,.0f} 元/月")
        
        return result
    
    def calculate_invest_amount(self, fund_code: str, current_holding: float, current_nav: float = None) -> dict:
        """
        计算当期投入金额
        
        Args:
            fund_code: 基金代码
            current_holding: 当前持仓市值
            current_nav: 当前净值（可选，用于计算份额）
        
        Returns:
            包含当期投入建议的结果字典
        """
        growth_result = self.calculate_target_growth(fund_code, current_holding)
        
        if "error" in growth_result:
            return growth_result
        
        target_growth = growth_result["target_growth"]
        
        invest_amount = target_growth
        
        growth_result["invest_amount"] = invest_amount
        growth_result["invest_action"] = "买入" if invest_amount > 0 else ("卖出" if invest_amount < 0 else "不操作")
        
        if current_nav and current_nav > 0:
            shares = abs(invest_amount) / current_nav
            growth_result["current_nav"] = current_nav
            growth_result["shares_to_trade"] = shares
        
        growth_result["algorithm_details"].append(f"")
        growth_result["algorithm_details"].append(f"【当期投入计算】")
        growth_result["algorithm_details"].append(f"每期投入金额 = 目标市值增长额")
        growth_result["algorithm_details"].append(f"            = {invest_amount:,.0f} 元")
        growth_result["algorithm_details"].append(f"操作建议: {growth_result['invest_action']}")
        
        return growth_result
    
    def simulate_period(self, fund_code: str, current_holding: float, months: int = 12) -> dict:
        """
        模拟多期定投过程
        
        Args:
            fund_code: 基金代码
            current_holding: 当前持仓市值
            months: 模拟月数
        
        Returns:
            模拟结果字典
        """
        growth_result = self.calculate_target_growth(fund_code, current_holding)
        
        if "error" in growth_result:
            return growth_result
        
        target_growth = growth_result["target_growth"]
        avg_monthly_return = growth_result["avg_monthly_return"]
        
        np.random.seed(42)
        simulated_returns = np.random.normal(avg_monthly_return, 6, months)
        
        target_value = current_holding
        current_value = current_holding
        
        records = []
        total_invested = 0
        total_sold = 0
        
        for i in range(months):
            target_value = target_value + target_growth
            
            monthly_return = simulated_returns[i]
            value_before_invest = current_value * (1 + monthly_return / 100)
            
            invest_amount = target_value - value_before_invest
            
            if invest_amount > 0:
                current_value = target_value
                total_invested += invest_amount
                action = "买入"
            else:
                current_value = target_value
                total_sold += abs(invest_amount)
                action = "卖出"
            
            records.append({
                "期数": i + 1,
                "目标市值": target_value,
                "模拟收益率": round(monthly_return, 2),
                "投入前市值": round(value_before_invest, 0),
                "投入金额": round(invest_amount, 0),
                "操作": action
            })
        
        growth_result["simulation"] = {
            "records": records,
            "total_invested": round(total_invested, 0),
            "total_sold": round(total_sold, 0),
            "net_invested": round(total_invested - total_sold, 0),
            "final_value": round(current_value, 0)
        }
        
        net_invest = total_invested - total_sold
        if current_holding + net_invest > 0:
            profit_rate = (current_value - current_holding - net_invest) / (current_holding + max(net_invest, 0)) * 100
            growth_result["simulation"]["profit_rate"] = round(profit_rate, 2)
        
        return growth_result
    
    def format_report(self, result: dict) -> str:
        """
        格式化输出报告
        """
        lines = []
        lines.append("=" * 70)
        lines.append("【市值定投计算报告】")
        lines.append("=" * 70)
        
        lines.append(f"\n基金代码: {result.get('fund_code', '未知')}")
        lines.append(f"基金名称: {result.get('fund_name', '未知')}")
        lines.append(f"基金类型: {result.get('fund_type', '未知')}")
        lines.append(f"成立日期: {result.get('establish_date', '未知')}")
        lines.append(f"成立年限: {result.get('fund_age_years', 0):.1f} 年")
        lines.append(f"当前持仓市值: {result.get('current_holding', 0):,.0f} 元")
        
        lines.append(f"\n" + "-" * 70)
        lines.append("【算法说明】")
        lines.append("-" * 70)
        lines.append(f"计算方法: {result.get('calculation_method', '未知')}")
        lines.append(f"参考来源: {result.get('reference_source', '未知')}")
        lines.append(f"当前市场阶段: {result.get('market_phase', '未知')}")
        
        if result.get('algorithm_details'):
            lines.append(f"\n计算过程:")
            for detail in result['algorithm_details']:
                lines.append(f"  {detail}")
        
        lines.append(f"\n" + "-" * 70)
        lines.append("【计算结果】")
        lines.append("-" * 70)
        lines.append(f"平均月收益率: {result.get('avg_monthly_return', 0):.2f}%")
        lines.append(f"目标市值增长额: {result.get('target_growth', 0):,.0f} 元/月")
        
        if 'invest_amount' in result:
            lines.append(f"\n当期投入金额: {result.get('invest_amount', 0):,.0f} 元")
            lines.append(f"操作建议: {result.get('invest_action', '未知')}")
        
        if 'simulation' in result:
            sim = result['simulation']
            lines.append(f"\n" + "-" * 70)
            lines.append("【模拟结果（12个月）】")
            lines.append("-" * 70)
            lines.append(f"累计买入: {sim.get('total_invested', 0):,.0f} 元")
            lines.append(f"累计卖出: {sim.get('total_sold', 0):,.0f} 元")
            lines.append(f"净投入: {sim.get('net_invested', 0):,.0f} 元")
            lines.append(f"最终市值: {sim.get('final_value', 0):,.0f} 元")
            if 'profit_rate' in sim:
                lines.append(f"累计收益率: {sim.get('profit_rate', 0):.2f}%")
        
        lines.append(f"\n" + "=" * 70)
        
        return "\n".join(lines)


def calculate_value_averaging(fund_code: str, current_holding: float, simulate: bool = False) -> dict:
    """
    便捷函数：计算市值定投
    
    Args:
        fund_code: 基金代码
        current_holding: 当前持仓市值
        simulate: 是否模拟多期
    
    Returns:
        计算结果字典
    """
    calc = ValueAveragingCalculator()
    
    if simulate:
        result = calc.simulate_period(fund_code, current_holding, months=12)
    else:
        result = calc.calculate_invest_amount(fund_code, current_holding)
    
    return result


def get_value_averaging_report(fund_code: str, current_holding: float, simulate: bool = True) -> str:
    """
    便捷函数：获取格式化的市值定投报告
    
    Args:
        fund_code: 基金代码
        current_holding: 当前持仓市值
        simulate: 是否模拟多期
    
    Returns:
        格式化的报告字符串
    """
    calc = ValueAveragingCalculator()
    
    if simulate:
        result = calc.simulate_period(fund_code, current_holding, months=12)
    else:
        result = calc.calculate_invest_amount(fund_code, current_holding)
    
    return calc.format_report(result)


def calculate_value_averaging_v2(
    fund_code: str,
    shares_at_base: float,
    nav_at_base: float,
    base_date: str,
    current_shares: float,
    current_nav: float,
    target_date: str = None,
    avg_monthly_return: float = None
) -> dict:
    """
    市值定投计算（修正版）- 支持任意日期回溯
    
    核心公式：
    1. 基准市值 = 基准日期持仓份额 × 基准日期净值
    2. 目标增长额 = 基准市值 × 平均月收益率 × (天数/30)
    3. 目标市值 = 基准市值 + 目标增长额
    4. 投入金额 = 目标市值 - 当前实际市值
    
    Args:
        fund_code: 基金代码
        shares_at_base: 基准日期持仓份额（从holding_history查询）
        nav_at_base: 基准日期净值
        base_date: 基准日期（格式：YYYY-MM-DD）
        current_shares: 当前持仓份额
        current_nav: 当前净值
        target_date: 目标日期（格式：YYYY-MM-DD，默认今天）
        avg_monthly_return: 平均月收益率（可选，不传则自动计算）
    
    Returns:
        计算结果字典
    """
    from datetime import datetime
    
    calc = ValueAveragingCalculator()
    
    # 设置默认目标日期
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # 计算天数差
    base_dt = datetime.strptime(base_date, '%Y-%m-%d')
    target_dt = datetime.strptime(target_date, '%Y-%m-%d')
    days_diff = (target_dt - base_dt).days
    
    # 如果没有传入平均月收益率，则自动计算
    if avg_monthly_return is None:
        # 首先检查缓存
        cached_return, is_fresh = calc._get_cached_fund_return(fund_code, CURRENT_PHASE)
        if is_fresh:
            avg_monthly_return = cached_return
        else:
            # 获取基金信息
            fund_info = calc.get_fund_info(fund_code)
            establish_date = fund_info.get('成立日期')
            
            if establish_date:
                establish_dt = pd.to_datetime(establish_date)
                fund_age_years = (datetime.now() - establish_dt).days / 365
            else:
                fund_age_years = 0
            
            if fund_age_years >= 5:
                # 使用基金自身历史数据
                nav_df = calc.get_fund_nav_history(fund_code, years=5)
                if nav_df is not None and len(nav_df) > 0:
                    monthly_df = calc.calculate_monthly_returns_from_nav(nav_df)
                    market_phases = calc.analyze_by_market_phase(monthly_df)
                    if CURRENT_PHASE in market_phases:
                        avg_monthly_return = market_phases[CURRENT_PHASE]['平均月收益率']
                    else:
                        avg_monthly_return = monthly_df['月收益率'].mean()
                    # 缓存结果
                    calc._cache_fund_return(fund_code, CURRENT_PHASE, avg_monthly_return)
                else:
                    avg_monthly_return = 1.0  # 默认值
            else:
                # 使用指数参考基准
                hs300_cached = calc._get_cached_benchmark(calc.hs300_code, CURRENT_PHASE)
                zz500_cached = calc._get_cached_benchmark(calc.zz500_code, CURRENT_PHASE)
                
                if hs300_cached.get('is_fresh') and zz500_cached.get('is_fresh'):
                    avg_monthly_return = (hs300_cached['avg_monthly_return'] + zz500_cached['avg_monthly_return']) / 2
                else:
                    # 重新计算基准
                    hs300_df = calc.get_etf_history(calc.hs300_code, years=5)
                    zz500_df = calc.get_etf_history(calc.zz500_code, years=5)
                    if hs300_df is not None and zz500_df is not None:
                        hs300_monthly = calc.calculate_monthly_returns_from_price(hs300_df)
                        zz500_monthly = calc.calculate_monthly_returns_from_price(zz500_df)
                        hs300_phases = calc.analyze_by_market_phase(hs300_monthly)
                        zz500_phases = calc.analyze_by_market_phase(zz500_monthly)
                        if CURRENT_PHASE in hs300_phases and CURRENT_PHASE in zz500_phases:
                            avg_monthly_return = (hs300_phases[CURRENT_PHASE]['平均月收益率'] + 
                                                zz500_phases[CURRENT_PHASE]['平均月收益率']) / 2
                        else:
                            avg_monthly_return = 1.0
                    else:
                        avg_monthly_return = 1.0
    
    # 核心计算
    base_value = shares_at_base * nav_at_base  # 基准市值
    monthly_factor = days_diff / 30.0  # 月数因子
    target_growth = base_value * avg_monthly_return / 100 * monthly_factor  # 目标增长额
    target_value = base_value + target_growth  # 目标市值
    
    # 当前实际市值（注意：用当前份额，不是基准份额）
    actual_value = current_shares * current_nav
    
    # 投入金额（正=买入，负=卖出）
    invest_amount = target_value - actual_value
    
    # 原有持仓的当前市值（用于计算原有持仓的盈亏）
    original_holding_value = shares_at_base * current_nav
    original_holding_profit = original_holding_value - base_value
    
    result = {
        "fund_code": fund_code,
        "base_date": base_date,
        "target_date": target_date,
        "days_diff": days_diff,
        "shares_at_base": shares_at_base,
        "nav_at_base": nav_at_base,
        "base_value": base_value,
        "current_shares": current_shares,
        "current_nav": current_nav,
        "actual_value": actual_value,
        "avg_monthly_return": avg_monthly_return,
        "monthly_factor": monthly_factor,
        "target_growth": target_growth,
        "target_value": target_value,
        "invest_amount": invest_amount,
        "invest_action": "买入" if invest_amount > 0 else ("卖出" if invest_amount < 0 else "不操作"),
        "original_holding_value": original_holding_value,
        "original_holding_profit": original_holding_profit,
        "market_phase": CURRENT_PHASE,
        "algorithm_details": [
            f"基准日期: {base_date}",
            f"目标日期: {target_date}",
            f"间隔天数: {days_diff}天",
            f"",
            f"【基准持仓】",
            f"基准日期份额: {shares_at_base:,.2f}份",
            f"基准日期净值: ¥{nav_at_base:.4f}",
            f"基准市值: ¥{base_value:,.2f}",
            f"",
            f"【当前持仓】",
            f"当前份额: {current_shares:,.2f}份",
            f"当前净值: ¥{current_nav:.4f}",
            f"当前市值: ¥{actual_value:,.2f}",
            f"",
            f"【原有持仓盈亏】",
            f"原有持仓现值: ¥{original_holding_value:,.2f}",
            f"原有持仓成本: ¥{base_value:,.2f}",
            f"原有持仓盈亏: ¥{original_holding_profit:,.2f}",
            f"",
            f"【目标计算】",
            f"平均月收益率: {avg_monthly_return:.2f}%",
            f"月数因子: {monthly_factor:.2f}",
            f"目标增长额: ¥{target_growth:,.2f}",
            f"目标市值: ¥{target_value:,.2f}",
            f"",
            f"【投资建议】",
            f"建议操作: {('买入' if invest_amount > 0 else '卖出') if invest_amount != 0 else '不操作'}",
            f"建议金额: ¥{abs(invest_amount):,.2f}",
        ]
    }
    
    return result


def get_shares_at_date(fund_code: str, portfolio_id: int, target_date: str) -> float:
    """
    查询指定日期持仓份额
    
    从holding_history表中查询指定日期之前的最新持仓记录
    
    Args:
        fund_code: 基金代码
        portfolio_id: 组合ID
        target_date: 目标日期（格式：YYYY-MM-DD）
    
    Returns:
        持仓份额，如果没有记录返回0
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT shares
                FROM holding_history 
                WHERE fund_code = ? AND portfolio_id = ? AND record_date <= ?
                ORDER BY record_date DESC, id DESC
                LIMIT 1
            ''', (fund_code, portfolio_id, target_date))
            row = cursor.fetchone()
            if row:
                return row['shares']
    except Exception as e:
        print(f"[ValueAveraging] 查询持仓失败: {e}")
    
    return 0.0


def get_nav_at_date(fund_code: str, target_date: str) -> float:
    """
    查询指定日期净值
    
    Args:
        fund_code: 基金代码
        target_date: 目标日期（格式：YYYY-MM-DD）
    
    Returns:
        净值，如果没有记录返回0
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT unit_nav 
                FROM fund_nav 
                WHERE fund_code = ? AND nav_date <= ?
                ORDER BY nav_date DESC
                LIMIT 1
            ''', (fund_code, target_date))
            row = cursor.fetchone()
            if row:
                return row['unit_nav']
    except Exception as e:
        print(f"[ValueAveraging] 查询净值失败: {e}")
    
    return 0.0


if __name__ == "__main__":
    # 测试新版算法
    result = calculate_value_averaging_v2(
        fund_code="000001",
        shares_at_base=1000,
        nav_at_base=10.0,
        base_date="2025-01-01",
        current_shares=1500,
        current_nav=11.0,
        target_date="2025-01-30",
        avg_monthly_return=1.15
    )
    print("\n".join(result['algorithm_details']))
