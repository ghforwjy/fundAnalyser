"""
测试使用AKShare官方数据的风险指标和业绩查询
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData, get_fund_risk_and_return, get_max_drawdown
from akshare_data_sync import sync_fund_risk_and_performance

def test_akshare_official_data():
    print("=" * 80)
    print("测试AKShare官方风险指标和业绩数据")
    print("=" * 80)
    
    smart = SmartFundData()
    
    # 步骤1: 同步000001的风险指标和业绩数据
    print("\n1. 同步000001的风险指标和业绩数据:")
    sync_fund_risk_and_performance('000001')
    
    # 步骤2: 查询风险指标
    print("\n2. 查询000001的风险指标:")
    risk_metrics = smart.get_fund_risk_metrics('000001')
    for metric in risk_metrics:
        print(f"   周期: {metric['period']}")
        print(f"     最大回撤: {metric['max_drawdown']}%")
        print(f"     夏普比率: {metric['sharpe_ratio']}")
        print(f"     年化波动率: {metric['annual_volatility']}%")
    
    # 步骤3: 查询业绩表现
    print("\n3. 查询000001的阶段业绩:")
    performance = smart.get_fund_performance('000001', perf_type='阶段业绩')
    for perf in performance[:5]:  # 只显示前5条
        print(f"   {perf['period']}: 收益率 {perf['period_return']}%")
    
    # 步骤4: 使用便捷函数查询单只基金
    print("\n4. 使用便捷函数get_max_drawdown查询单只基金:")
    max_dd = get_max_drawdown('000001', period='近1年')
    print(f"   000001 近1年最大回撤: {max_dd}%")
    
    # 步骤5: 同步并查询中航基金
    print("\n5. 同步中航基金的风险指标和业绩数据（测试3只）:")
    test_codes = ['004926', '004927', '018956']
    sync_fund_risk_and_performance(fund_codes=test_codes)
    
    print("\n6. 查询中航基金风险收益数据:")
    results = get_fund_risk_and_return(keyword='中航', period='近1年')
    print(f"   返回 {len(results)} 条记录")
    for r in results[:3]:
        print(f"   {r['fund_code']} - {r['fund_name']}")
        print(f"     近1年收益率: {r['period_return']}%")
        print(f"     近1年最大回撤: {r['max_drawdown']}%")
        print(f"     夏普比率: {r['sharpe_ratio']}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

if __name__ == '__main__':
    test_akshare_official_data()
