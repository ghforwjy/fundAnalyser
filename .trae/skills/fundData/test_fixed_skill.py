"""
测试修正后的skill功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData, get_max_drawdown

def test_fixed_queries():
    print("=" * 80)
    print("测试修正后的skill功能")
    print("=" * 80)
    
    smart = SmartFundData()
    
    # 测试1: 使用query_funds_by_keyword查询中航基金
    print("\n1. 使用query_funds_by_keyword查询中航基金:")
    funds = smart.query_funds_by_keyword('中航')
    print(f"   找到 {len(funds)} 只中航基金")
    
    # 筛选权益类
    equity_funds = []
    for f in funds:
        fund_type = f['fund_type']
        is_equity = ('股票型' in fund_type or '混合型' in fund_type or '指数型-股票' in fund_type)
        is_exclude = any(kw in fund_type for kw in ['债券', '货币', '固收', '存单'])
        if is_equity and not is_exclude:
            equity_funds.append(f)
    print(f"   其中权益类基金 {len(equity_funds)} 只")
    
    # 显示领航系列
    linghang = [f for f in equity_funds if '领航' in f['fund_name']]
    print(f"   领航系列基金 {len(linghang)} 只:")
    for f in linghang[:5]:
        print(f"     {f['fund_code']} - {f['fund_name']}")
    
    # 测试2: 计算单只基金最大回撤
    print("\n2. 计算单只基金最大回撤（近1年）:")
    result = smart.calculate_max_drawdown('000001', period='1y')
    print(f"   基金: {result['fund_code']}")
    print(f"   周期: {result['period']}")
    print(f"   最大回撤: {result['max_drawdown']}%")
    print(f"   峰值日期: {result['peak_date']}")
    print(f"   谷值日期: {result['trough_date']}")
    
    # 测试3: 批量计算最大回撤（只测试3只）
    print("\n3. 批量计算最大回撤（测试3只中航基金）:")
    test_codes = [f['fund_code'] for f in equity_funds[:3]]
    results = smart.get_funds_max_drawdown(fund_codes=test_codes, period='1y')
    for r in results:
        if r.get('max_drawdown'):
            print(f"   {r['fund_code']} - {r['fund_name']}: 最大回撤 {r['max_drawdown']}%")
    
    # 测试4: 便捷函数
    print("\n4. 使用便捷函数get_max_drawdown:")
    result = get_max_drawdown('000001', period='1y')
    print(f"   000001 最大回撤: {result['max_drawdown']}%")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

if __name__ == '__main__':
    test_fixed_queries()
