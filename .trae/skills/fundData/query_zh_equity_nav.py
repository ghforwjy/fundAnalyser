"""
查询中航基金权益类基金最新净值（排除债券基金）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData

def query_zh_equity_nav():
    """查询中航基金权益类基金最新净值"""
    smart = SmartFundData()
    
    print("=" * 100)
    print("中航基金权益类基金最新净值列表（排除债券基金）")
    print("=" * 100)
    
    # 查询中航基金，排除债券类型
    print("\n正在查询中航基金权益类基金...")
    
    # 先查询所有中航基金
    all_zh_funds = smart.query_funds(company='中航', limit=100)
    
    # 筛选权益类基金（排除债券型、货币型、固收型等）
    # 只保留真正的权益类：股票型、混合型（偏股/灵活）、指数型-股票
    equity_funds = []
    for fund in all_zh_funds:
        fund_type = fund['fund_type']
        
        # 明确的权益类类型
        is_equity = (
            '股票型' in fund_type or
            ('混合型' in fund_type and any(x in fund_type for x in ['偏股', '灵活', '配置'])) or
            ('指数型-股票' in fund_type)
        )
        
        # 排除债券、货币、固收、存单等
        is_exclude = any(kw in fund_type for kw in ['债券', '货币', '理财', '现金', '固收', '存单'])
        
        if is_equity and not is_exclude:
            equity_funds.append(fund)
    
    print(f"找到 {len(equity_funds)} 只权益类基金（已排除债券基金）\n")
    
    if not equity_funds:
        print("未找到中航基金权益类基金")
        return
    
    # 获取基金代码列表
    fund_codes = [f['fund_code'] for f in equity_funds]
    
    # 批量获取最新净值（智能缓存）
    print("正在获取最新净值数据...")
    nav_list = smart.get_funds_nav_list(
        fund_codes=fund_codes,
        force_update=False  # 使用智能缓存
    )
    
    # 按基金类型分组
    funds_by_type = {}
    for item in nav_list:
        fund_type = item['fund_type']
        if fund_type not in funds_by_type:
            funds_by_type[fund_type] = []
        funds_by_type[fund_type].append(item)
    
    # 显示结果
    print("\n" + "=" * 100)
    print(f"{'基金代码':<10} {'基金名称':<40} {'基金类型':<15} {'净值日期':<12} {'单位净值':<10} {'日涨跌':<8}")
    print("-" * 100)
    
    # 按类型分组显示
    for fund_type in sorted(funds_by_type.keys()):
        funds = funds_by_type[fund_type]
        print(f"\n【{fund_type}】共 {len(funds)} 只")
        print("-" * 100)
        
        for item in funds:
            name = item['fund_name'][:37] + '..' if len(item['fund_name']) > 39 else item['fund_name']
            fund_type_short = item['fund_type'][:13] if len(item['fund_type']) > 15 else item['fund_type']
            nav_date = item['nav_date'] if item['nav_date'] else '--'
            unit_nav = f"{item['unit_nav']:.4f}" if item['unit_nav'] else '--'
            daily_return = f"{item['daily_return']:.2f}%" if item['daily_return'] else '--'
            
            print(f"{item['fund_code']:<10} {name:<40} {fund_type_short:<15} {nav_date:<12} {unit_nav:<10} {daily_return:<8}")
    
    print("=" * 100)
    
    # 统计信息
    print(f"\n统计信息:")
    print(f"  权益类基金总数: {len(equity_funds)} 只")
    print(f"  数据日期: {nav_list[0]['nav_date'] if nav_list else '--'}")
    
    # 涨跌统计
    up_count = sum(1 for item in nav_list if item['daily_return'] and item['daily_return'] > 0)
    down_count = sum(1 for item in nav_list if item['daily_return'] and item['daily_return'] < 0)
    flat_count = len(nav_list) - up_count - down_count
    
    print(f"\n涨跌分布:")
    print(f"  上涨: {up_count} 只")
    print(f"  下跌: {down_count} 只")
    print(f"  平盘: {flat_count} 只")
    
    # 涨幅前三
    sorted_by_return = sorted([i for i in nav_list if i['daily_return']], 
                              key=lambda x: x['daily_return'], reverse=True)
    
    if sorted_by_return:
        print(f"\n涨幅前三:")
        for i, item in enumerate(sorted_by_return[:3], 1):
            print(f"  {i}. {item['fund_code']} {item['fund_name']}: +{item['daily_return']:.2f}%")
        
        print(f"\n跌幅前三:")
        for i, item in enumerate(sorted_by_return[-3:], 1):
            print(f"  {i}. {item['fund_code']} {item['fund_name']}: {item['daily_return']:.2f}%")

if __name__ == '__main__':
    query_zh_equity_nav()
