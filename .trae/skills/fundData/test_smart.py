"""
测试 SmartFundData 智能接口
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData, query_funds_nav, get_fund_nav

def test_smart_interface():
    print("=" * 80)
    print("SmartFundData 智能接口测试")
    print("=" * 80)
    
    smart = SmartFundData()
    
    # 测试1: 通用查询 - 中航基金
    print("\n1. 通用查询 - 中航基金权益类:")
    funds = smart.query_funds(company='中航', fund_type='股票', limit=5)
    print(f"   找到 {len(funds)} 只基金")
    for f in funds[:3]:
        print(f"   {f['fund_code']} - {f['fund_name']}")
    
    # 测试2: 使用便捷函数查询中航基金净值
    print("\n2. 便捷函数 - 查询中航基金最新净值（首次）:")
    results = query_funds_nav(company='中航', fund_type='混合')
    print(f"   返回 {len(results)} 条记录")
    for r in results[:3]:
        print(f"   {r['fund_code']} - {r['fund_name']}: {r.get('unit_nav', 'N/A')}")
    
    # 测试3: 再次查询（应该使用缓存）
    print("\n3. 再次查询（应该使用缓存）:")
    results = query_funds_nav(company='中航', fund_type='混合')
    print(f"   返回 {len(results)} 条记录")
    
    # 测试4: 单只基金查询
    print("\n4. 单只基金查询 - 000001:")
    nav = get_fund_nav('000001')
    if nav:
        print(f"   最新净值: {nav['unit_nav']} ({nav['nav_date']})")
    
    # 测试5: 再次查询单只基金（缓存）
    print("\n5. 再次查询单只基金（应该使用缓存）:")
    nav = get_fund_nav('000001')
    if nav:
        print(f"   最新净值: {nav['unit_nav']} ({nav['nav_date']})")
    
    # 测试6: 净值历史查询
    print("\n6. 查询净值历史（最近10天）:")
    history = smart.query_nav_history('000001', days=10)
    print(f"   返回 {len(history)} 条记录")
    for h in history[:3]:
        print(f"   {h['nav_date']}: {h['unit_nav']}")
    
    # 测试7: 数据汇总
    print("\n7. 数据汇总统计:")
    summary = smart.get_nav_summary()
    print(f"   总基金数: {summary['total_funds']}")
    print(f"   净值覆盖: {summary['nav_coverage']} ({summary['coverage_rate']})")
    print(f"   最新净值日期: {summary['latest_nav_date']}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

if __name__ == '__main__':
    test_smart_interface()
