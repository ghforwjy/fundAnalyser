"""
测算目标市值增长额

算法逻辑：
1. 基金成立≥5年：用该基金历史数据，按牛熊市阶段计算平均月收益率
2. 基金成立<5年：用沪深300/中证500指数作为参考基准

目标市值增长额 = 当前持仓市值 × 平均月收益率
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


MARKET_PHASES = {
    "牛市尾声": ("2021-01", "2021-02"),
    "熊市": ("2021-03", "2023-12"),
    "牛市": ("2024-01", "2025-12")
}

CURRENT_PHASE = "牛市"


def get_fund_info(fund_code: str) -> dict:
    """
    获取基金基本信息，包括成立日期
    """
    try:
        df = ak.fund_overview_em(symbol=fund_code)
        if df is not None and len(df) > 0:
            row = df.iloc[0]
            info = {
                '基金全称': row['基金全称'],
                '基金简称': row['基金简称'],
                '基金类型': row['基金类型'],
                '发行日期': row['发行日期'],
                '成立日期/规模': row['成立日期/规模'],
            }
            
            establish_str = row['成立日期/规模']
            if '/' in str(establish_str):
                date_part = establish_str.split('/')[0].strip()
                import re
                match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_part)
                if match:
                    info['成立日期'] = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
            
            return info
        return {}
    except Exception as e:
        print(f"获取基金信息失败: {e}")
        return {}


def get_fund_nav_history(fund_code: str, years: int = 5) -> pd.DataFrame:
    """
    获取基金历史净值数据
    """
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        df['净值日期'] = pd.to_datetime(df['净值日期'])
        df = df.sort_values('净值日期')
        return df
    except Exception as e:
        print(f"获取基金净值失败: {e}")
        return None


def get_etf_history(etf_code: str, years: int = 5) -> pd.DataFrame:
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
        print(f"获取ETF数据失败: {e}")
        return None


def calculate_monthly_returns_from_nav(df: pd.DataFrame, date_col: str = "净值日期", nav_col: str = "单位净值") -> pd.DataFrame:
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


def calculate_monthly_returns_from_price(df: pd.DataFrame, date_col: str = "日期", price_col: str = "收盘") -> pd.DataFrame:
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


def analyze_by_market_phase(monthly_df: pd.DataFrame) -> dict:
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


def simulate_value_averaging(fund_code: str, current_holding: float, months: int = 12):
    """
    模拟市值定投过程
    
    完整公式：
    1. 目标市值增长额 = 当前持仓市值 × 平均月收益率
    2. 每期目标市值 = 上期目标市值 + 目标市值增长额
    3. 每期投入金额 = 目标市值 - 当前市值
    
    Args:
        fund_code: 基金代码
        current_holding: 当前持仓市值
        months: 模拟月数
    """
    print(f"\n{'='*70}")
    print(f"基金代码: {fund_code}")
    print(f"当前持仓市值: {current_holding:,.0f} 元")
    print(f"模拟周期: {months} 个月")
    print(f"{'='*70}")
    
    fund_info = get_fund_info(fund_code)
    
    establish_date = None
    if '成立日期' in fund_info:
        try:
            establish_date = pd.to_datetime(fund_info['成立日期'])
            print(f"基金名称: {fund_info.get('基金简称', '未知')}")
            print(f"基金类型: {fund_info.get('基金类型', '未知')}")
            print(f"基金成立日期: {fund_info['成立日期']}")
        except:
            pass
    
    today = datetime.now()
    fund_age_years = 0
    if establish_date:
        fund_age_years = (today - establish_date).days / 365
    
    print(f"基金成立年限: {fund_age_years:.1f} 年")
    
    avg_monthly_return = 0
    
    if fund_age_years >= 5:
        print(f"\n>>> 基金成立≥5年，使用该基金历史数据计算")
        
        nav_df = get_fund_nav_history(fund_code, years=5)
        if nav_df is None or len(nav_df) == 0:
            return {"error": "无法获取基金净值数据"}
        
        monthly_df = calculate_monthly_returns_from_nav(nav_df)
        market_phases = analyze_by_market_phase(monthly_df)
        
        print(f"\n各市场阶段收益率分析:")
        for phase, stats in market_phases.items():
            print(f"  {phase}: 平均月收益率 {stats['平均月收益率']:.2f}%, 标准差 {stats['月收益率标准差']:.2f}%")
        
        if CURRENT_PHASE in market_phases:
            avg_monthly_return = market_phases[CURRENT_PHASE]['平均月收益率']
        else:
            avg_monthly_return = monthly_df['月收益率'].mean()
        
        print(f"\n当前市场阶段: {CURRENT_PHASE}")
        print(f"使用平均月收益率: {avg_monthly_return:.2f}%")
        
    else:
        print(f"\n>>> 基金成立<5年，使用沪深300/中证500作为参考基准")
        
        print(f"\n--- 沪深300ETF (510300) ---")
        hs300_df = get_etf_history("510300", years=3)
        hs300_monthly = calculate_monthly_returns_from_price(hs300_df)
        hs300_avg = hs300_monthly['月收益率'].mean()
        hs300_std = hs300_monthly['月收益率'].std()
        print(f"近3年平均月收益率: {hs300_avg:.2f}%")
        print(f"近3年月收益率标准差: {hs300_std:.2f}%")
        
        print(f"\n--- 中证500ETF (510500) ---")
        zz500_df = get_etf_history("510500", years=3)
        zz500_monthly = calculate_monthly_returns_from_price(zz500_df)
        zz500_avg = zz500_monthly['月收益率'].mean()
        zz500_std = zz500_monthly['月收益率'].std()
        print(f"近3年平均月收益率: {zz500_avg:.2f}%")
        print(f"近3年月收益率标准差: {zz500_std:.2f}%")
        
        avg_monthly_return = (hs300_avg + zz500_avg) / 2
        
        print(f"\n综合参考基准:")
        print(f"平均月收益率: {avg_monthly_return:.2f}%")
    
    target_growth = current_holding * avg_monthly_return / 100
    
    print(f"\n{'='*70}")
    print(f"【第一步】计算目标市值增长额")
    print(f"{'='*70}")
    print(f"公式: 目标市值增长额 = 当前持仓市值 × 平均月收益率")
    print(f"计算: {current_holding:,.0f} × {avg_monthly_return:.2f}% = {target_growth:,.0f} 元/月")
    
    print(f"\n{'='*70}")
    print(f"【第二步】模拟定投过程")
    print(f"{'='*70}")
    print(f"公式: 每期投入金额 = 目标市值 - 当前市值")
    print(f"      目标市值 = 上期目标市值 + 目标市值增长额")
    
    np.random.seed(42)
    simulated_returns = np.random.normal(avg_monthly_return, 6, months)
    
    target_value = current_holding
    current_value = current_holding
    
    records = []
    total_invested = 0
    total_sold = 0
    
    print(f"\n{'期数':<4} {'目标市值':>12} {'模拟收益率':>10} {'投入前市值':>12} {'投入金额':>12} {'操作':<6}")
    print("-" * 68)
    
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
            "模拟收益率": monthly_return,
            "投入前市值": value_before_invest,
            "投入金额": invest_amount,
            "操作": action
        })
        
        invest_display = f"+{invest_amount:,.0f}" if invest_amount > 0 else f"{invest_amount:,.0f}"
        print(f"{i+1:<4} {target_value:>12,.0f} {monthly_return:>9.2f}% {value_before_invest:>12,.0f} {invest_display:>12} {action:<6}")
    
    print("-" * 68)
    print(f"\n{'='*70}")
    print(f"【汇总】")
    print(f"{'='*70}")
    print(f"初始市值: {current_holding:,.0f} 元")
    print(f"目标市值增长额: {target_growth:,.0f} 元/月")
    print(f"累计买入金额: {total_invested:,.0f} 元")
    print(f"累计卖出金额: {total_sold:,.0f} 元")
    print(f"净投入金额: {total_invested - total_sold:,.0f} 元")
    print(f"最终市值: {current_value:,.0f} 元")
    
    net_invest = total_invested - total_sold
    if current_holding + net_invest > 0:
        profit_rate = (current_value - current_holding - net_invest) / (current_holding + max(net_invest, 0)) * 100
        print(f"累计收益率: {profit_rate:.2f}%")
    
    return {
        "fund_code": fund_code,
        "fund_age_years": fund_age_years,
        "current_holding": current_holding,
        "avg_monthly_return": avg_monthly_return,
        "target_growth": target_growth,
        "total_invested": total_invested,
        "total_sold": total_sold,
        "final_value": current_value,
        "records": records
    }


def main():
    """
    测试市值定投完整流程
    """
    print("="*70)
    print("市值定投法 - 完整流程模拟")
    print("="*70)
    print(f"测算时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前市场阶段: {CURRENT_PHASE}")
    
    print("\n" + "="*70)
    print("核心公式")
    print("="*70)
    print("""
    【第一步】计算目标市值增长额
        目标市值增长额 = 当前持仓市值 × 平均月收益率
    
    【第二步】每月定投计算
        目标市值 = 上期目标市值 + 目标市值增长额
        每期投入金额 = 目标市值 - 当前市值
        
        若投入金额 > 0：买入
        若投入金额 < 0：卖出
        若投入金额 = 0：不操作
    """)
    
    test_cases = [
        ("000001", 50000, 12, "华夏成长混合 - 成立≥5年"),
        ("510300", 100000, 12, "沪深300ETF - 成立≥5年"),
    ]
    
    results = []
    
    for fund_code, current_holding, months, description in test_cases:
        print(f"\n\n{'#'*70}")
        print(f"# {description}")
        print(f"{'#'*70}")
        
        result = simulate_value_averaging(fund_code, current_holding, months)
        result['description'] = description
        results.append(result)
    
    print(f"\n\n{'='*70}")
    print("测算结果汇总")
    print(f"{'='*70}")
    print(f"{'基金代码':<10} {'目标增长额':<12} {'累计买入':<12} {'累计卖出':<12} {'净投入':<12}")
    print("-"*70)
    for r in results:
        if 'error' not in r:
            net_invest = r['total_invested'] - r.get('total_sold', 0)
            print(f"{r['fund_code']:<10} {r['target_growth']:>10,.0f}元 {r['total_invested']:>10,.0f}元 {r.get('total_sold', 0):>10,.0f}元 {net_invest:>10,.0f}元")


if __name__ == "__main__":
    main()
