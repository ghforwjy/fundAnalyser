"""
查询所有中航基金权益类基金（修正版）
通过基金名称关键词"中航"来查询
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData

def query_all_zh_equity():
    """查询所有中航基金权益类基金"""
    smart = SmartFundData()
    
    print("=" * 110)
    print("中航基金权益类基金最新净值列表（通过基金名称筛选）")
    print("=" * 110)
    
    # 通过基金名称关键词"中航"查询所有中航基金
    print("\n正在查询所有中航基金...")
    all_zh_funds = smart.query_funds(keyword='中航', limit=200)
    
    print(f"找到 {len(all_zh_funds)} 只名称包含'中航'的基金")
    
    # 筛选权益类基金（排除债券型、货币型、固收型等）
    # 权益类包括：股票型、混合型（各种细分类型）、指数型-股票
    equity_funds = []
    for fund in all_zh_funds:
        fund_type = fund['fund_type']
        
        # 权益类定义：
        # 1. 股票型（所有股票型都是权益类）
        # 2. 混合型（所有混合型都是权益类，包括偏股、灵活、平衡等）
        # 3. 指数型-股票（股票指数）
        is_equity = (
            '股票型' in fund_type or
            '混合型' in fund_type or
            '指数型-股票' in fund_type
        )
        
        # 排除债券、货币、固收、存单等
        is_exclude = any(kw in fund_type for kw in ['债券', '货币', '理财', '现金', '固收', '存单'])
        
        if is_equity and not is_exclude:
            equity_funds.append(fund)
    
    print(f"其中权益类基金 {len(equity_funds)} 只（已排除债券、货币等）\n")
    
    if not equity_funds:
        print("未找到中航基金权益类基金")
        return
    
    # 显示所有权益类基金
    print("中航基金权益类基金清单：")
    print("-" * 110)
    for i, f in enumerate(equity_funds, 1):
        print(f"{i:2d}. {f['fund_code']} - {f['fund_name']} ({f['fund_type']})")
    print("-" * 110)
    
    # 获取基金代码列表
    fund_codes = [f['fund_code'] for f in equity_funds]
    
    # 批量获取最新净值（智能缓存）
    print("\n正在获取最新净值数据...")
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
    print("\n" + "=" * 110)
    print(f"{'基金代码':<10} {'基金名称':<45} {'基金类型':<18} {'净值日期':<12} {'单位净值':<10} {'日涨跌':<8}")
    print("-" * 110)
    
    # 按类型分组显示
    for fund_type in sorted(funds_by_type.keys()):
        funds = funds_by_type[fund_type]
        print(f"\n【{fund_type}】共 {len(funds)} 只")
        print("-" * 110)
        
        for item in funds:
            name = item['fund_name'][:42] + '..' if len(item['fund_name']) > 44 else item['fund_name']
            fund_type_short = item['fund_type'][:15] if len(item['fund_type']) > 17 else item['fund_type']
            nav_date = item['nav_date'] if item['nav_date'] else '--'
            unit_nav = f"{item['unit_nav']:.4f}" if item['unit_nav'] else '--'
            daily_return = f"{item['daily_return']:.2f}%" if item['daily_return'] else '--'
            
            print(f"{item['fund_code']:<10} {name:<45} {fund_type_short:<18} {nav_date:<12} {unit_nav:<10} {daily_return:<8}")
    
    print("=" * 110)
    
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
    
    # 涨跌幅排行
    sorted_by_return = sorted([i for i in nav_list if i['daily_return']], 
                              key=lambda x: x['daily_return'], reverse=True)
    
    if sorted_by_return:
        print(f"\n涨幅前三:")
        for i, item in enumerate(sorted_by_return[:3], 1):
            print(f"  {i}. {item['fund_code']} {item['fund_name']}: +{item['daily_return']:.2f}%")
        
        print(f"\n跌幅前三:")
        for i, item in enumerate(sorted_by_return[-3:], 1):
            print(f"  {i}. {item['fund_code']} {item['fund_name']}: {item['daily_return']:.2f}%")
    
    # 特别标注领航系列
    linghang_funds = [f for f in equity_funds if '领航' in f['fund_name']]
    if linghang_funds:
        print(f"\n\n★ 中航领航系列基金（{len(linghang_funds)} 只）:")
        for f in linghang_funds:
            print(f"  - {f['fund_code']} {f['fund_name']}")

if __name__ == '__main__':
    query_all_zh_equity()
