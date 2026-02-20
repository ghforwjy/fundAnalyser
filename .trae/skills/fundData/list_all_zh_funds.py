"""
列出所有中航证券权益类基金
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill

def list_all_zh_funds():
    skill = FundDataSkill()
    
    # 搜索中航证券的基金
    print('=== 中航证券所有权益类基金列表 ===\n')
    results = skill.search_funds('中航', 100)
    
    # 筛选权益类基金
    equity_types = ['股票', '混合', '指数']
    zh_funds = []
    for r in results:
        if '中航' in r['fund_name'] or '中航' in r['company_name']:
            if any(t in r['fund_type'] for t in equity_types):
                zh_funds.append(r)
    
    # 按类型分组
    funds_by_type = {}
    for f in zh_funds:
        fund_type = f['fund_type']
        if fund_type not in funds_by_type:
            funds_by_type[fund_type] = []
        funds_by_type[fund_type].append(f)
    
    # 显示统计
    print(f'总计: {len(zh_funds)} 只权益类基金\n')
    print('按类型分布:')
    for fund_type, funds in sorted(funds_by_type.items(), key=lambda x: -len(x[1])):
        print(f'  {fund_type}: {len(funds)} 只')
    
    print('\n' + '=' * 100)
    print(f'{"序号":<6} {"基金代码":<10} {"基金名称":<45} {"基金类型":<20}')
    print('=' * 100)
    
    # 显示所有基金
    for i, f in enumerate(zh_funds, 1):
        name = f['fund_name'][:42] + '..' if len(f['fund_name']) > 44 else f['fund_name']
        print(f'{i:<6} {f["fund_code"]:<10} {name:<45} {f["fund_type"]:<20}')
    
    print('=' * 100)
    
    # 保存基金代码列表供后续使用
    codes = [f['fund_code'] for f in zh_funds]
    print(f'\n基金代码列表（共{len(codes)}只）:')
    print(codes)

if __name__ == '__main__':
    list_all_zh_funds()
