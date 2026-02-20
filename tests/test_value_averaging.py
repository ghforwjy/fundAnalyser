"""
测试市值定投法所需的历史收益率数据获取和计算

目标：
1. 验证akshare接口能否获取历史净值数据
2. 测试沪深300、中证500等指数的收益率数据
3. 计算不同市场环境下的平均月度收益率
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def test_fund_nav_history(fund_code: str, years: int = 5):
    """
    测试获取基金历史净值数据
    
    Args:
        fund_code: 基金代码
        years: 回溯年数
    """
    print(f"\n{'='*60}")
    print(f"测试基金 {fund_code} 历史净值数据获取")
    print(f"{'='*60}")
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        
        if df is not None and len(df) > 0:
            print(f"获取成功，共 {len(df)} 条记录")
            print(f"数据时间范围: {df.iloc[0, 0]} 至 {df.iloc[-1, 0]}")
            print(f"\n最近5条记录:")
            print(df.tail())
            return df
        else:
            print("获取失败或数据为空")
            return None
    except Exception as e:
        print(f"获取失败: {e}")
        return None


def test_etf_history(etf_code: str, years: int = 5):
    """
    测试获取ETF历史行情数据
    
    Args:
        etf_code: ETF代码
        years: 回溯年数
    """
    print(f"\n{'='*60}")
    print(f"测试ETF {etf_code} 历史行情数据获取")
    print(f"{'='*60}")
    
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
        
        if df is not None and len(df) > 0:
            print(f"获取成功，共 {len(df)} 条记录")
            print(f"数据时间范围: {df.iloc[0, 0]} 至 {df.iloc[-1, 0]}")
            print(f"\n最近5条记录:")
            print(df.tail())
            return df
        else:
            print("获取失败或数据为空")
            return None
    except Exception as e:
        print(f"获取失败: {e}")
        return None


def test_index_fund_rank():
    """
    测试获取指数型基金排行数据（包含收益率指标）
    """
    print(f"\n{'='*60}")
    print(f"测试指数型基金排行数据获取")
    print(f"{'='*60}")
    
    try:
        df = ak.fund_info_index_em(symbol="沪深指数", indicator="被动指数型")
        
        if df is not None and len(df) > 0:
            print(f"获取成功，共 {len(df)} 条记录")
            print(f"\n列名: {df.columns.tolist()}")
            print(f"\n前3条记录:")
            print(df.head(3))
            return df
        else:
            print("获取失败或数据为空")
            return None
    except Exception as e:
        print(f"获取失败: {e}")
        return None


def calculate_monthly_returns(df: pd.DataFrame, date_col: str = "净值日期", nav_col: str = "单位净值") -> pd.DataFrame:
    """
    计算月度收益率
    
    Args:
        df: 净值数据DataFrame
        date_col: 日期列名
        nav_col: 净值列名
    """
    print(f"\n{'='*60}")
    print(f"计算月度收益率")
    print(f"{'='*60}")
    
    try:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        df['月份'] = df[date_col].dt.to_period('M')
        
        monthly_df = df.groupby('月份').agg({
            nav_col: ['first', 'last']
        }).reset_index()
        
        monthly_df.columns = ['月份', '月初净值', '月末净值']
        monthly_df['月收益率'] = (monthly_df['月末净值'] / monthly_df['月初净值'] - 1) * 100
        
        print(f"共计算 {len(monthly_df)} 个月的收益率")
        print(f"\n月收益率统计:")
        print(f"  平均月收益率: {monthly_df['月收益率'].mean():.2f}%")
        print(f"  月收益率中位数: {monthly_df['月收益率'].median():.2f}%")
        print(f"  月收益率标准差: {monthly_df['月收益率'].std():.2f}%")
        print(f"  最大月收益率: {monthly_df['月收益率'].max():.2f}%")
        print(f"  最小月收益率: {monthly_df['月收益率'].min():.2f}%")
        
        return monthly_df
    except Exception as e:
        print(f"计算失败: {e}")
        return None


def analyze_by_market_phase(monthly_df: pd.DataFrame) -> dict:
    """
    按牛熊市阶段分析收益率
    
    牛熊市划分（基于市场共识）：
    - 2021年1月-2月：牛市尾声
    - 2021年2月-2023年12月：熊市
    - 2024年1月-2025年12月：牛市
    """
    print(f"\n{'='*60}")
    print(f"按牛熊市阶段分析收益率")
    print(f"{'='*60}")
    
    market_phases = {
        "牛市尾声": ("2021-01", "2021-02"),
        "熊市": ("2021-03", "2023-12"),
        "牛市": ("2024-01", "2025-12")
    }
    
    results = {}
    
    for phase_name, (start, end) in market_phases.items():
        try:
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
                
                print(f"\n{phase_name} ({start} ~ {end}):")
                print(f"  月数: {count}")
                print(f"  平均月收益率: {avg_return:.2f}%")
                print(f"  月收益率标准差: {std_return:.2f}%")
        except Exception as e:
            print(f"分析 {phase_name} 失败: {e}")
    
    return results


def calculate_target_growth_rate(market_phases: dict, current_phase: str = "牛市") -> float:
    """
    根据市场阶段计算目标市值增长额的建议增长率
    
    Args:
        market_phases: 各市场阶段的收益率统计
        current_phase: 当前市场阶段
    
    Returns:
        建议的月度增长率（百分比）
    """
    print(f"\n{'='*60}")
    print(f"计算目标市值增长额的建议增长率")
    print(f"{'='*60}")
    
    if current_phase in market_phases:
        current_return = market_phases[current_phase]["平均月收益率"]
        current_std = market_phases[current_phase]["月收益率标准差"]
        
        conservative_return = current_return - current_std * 0.5
        
        print(f"当前市场阶段: {current_phase}")
        print(f"历史平均月收益率: {current_return:.2f}%")
        print(f"历史月收益率标准差: {current_std:.2f}%")
        print(f"保守估计月收益率（均值-0.5倍标准差）: {conservative_return:.2f}%")
        
        return conservative_return
    else:
        print(f"未找到 {current_phase} 阶段的数据")
        return 0.0


def test_hs300_index():
    """
    测试沪深300指数相关ETF数据
    沪深300ETF代码: 510300
    """
    print(f"\n{'='*60}")
    print(f"测试沪深300ETF (510300) 数据")
    print(f"{'='*60}")
    
    return test_etf_history("510300", years=5)


def test_zz500_index():
    """
    测试中证500指数相关ETF数据
    中证500ETF代码: 510500
    """
    print(f"\n{'='*60}")
    print(f"测试中证500ETF (510500) 数据")
    print(f"{'='*60}")
    
    return test_etf_history("510500", years=5)


def main():
    """
    主测试函数
    """
    print("="*60)
    print("市值定投法 - 历史收益率数据测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_fund = "000001"
    fund_df = test_fund_nav_history(test_fund, years=5)
    
    if fund_df is not None:
        monthly_df = calculate_monthly_returns(fund_df)
        
        if monthly_df is not None:
            market_phases = analyze_by_market_phase(monthly_df)
            
            target_growth = calculate_target_growth_rate(market_phases, current_phase="牛市")
    
    hs300_df = test_hs300_index()
    
    zz500_df = test_zz500_index()
    
    index_rank_df = test_index_fund_rank()
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
