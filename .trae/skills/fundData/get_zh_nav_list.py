"""
获取中航基金所有权益类基金最新净值列表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill
import time

def get_zh_nav_list():
    skill = FundDataSkill()
    
    # 搜索中航基金
    print('正在查询中航基金权益类基金...')
    results = skill.search_funds('中航', 100)
    
    # 筛选权益类基金
    equity_types = ['股票', '混合', '指数']
    zh_funds = []
    for r in results:
        if '中航' in r['fund_name'] or '中航' in r['company_name']:
            if any(t in r['fund_type'] for t in equity_types):
                zh_funds.append(r)
    
    if not zh_funds:
        print('未找到中航基金权益类基金')
        return
    
    print(f'找到 {len(zh_funds)} 只中航基金权益类基金')
    print('正在获取最新净值数据...\n')
    
    # 逐个获取净值
    nav_list = []
    for i, fund in enumerate(zh_funds, 1):
        code = fund['fund_code']
        print(f'[{i}/{len(zh_funds)}] 获取 {code} {fund["fund_name"]}...', end=' ')
        
        try:
            # 同步净值
            result = skill.sync_group_nav([code])
            
            # 查询最新净值
            nav_data = skill.query_fund_nav(code, limit=1)
            if nav_data:
                nav = nav_data[0]
                nav_list.append({
                    'code': code,
                    'name': fund['fund_name'],
                    'type': fund['fund_type'],
                    'nav_date': nav['nav_date'],
                    'unit_nav': nav['unit_nav'],
                    'accum_nav': nav['accum_nav'],
                    'daily_return': nav['daily_return']
                })
                print(f'✓ 净值: {nav["unit_nav"]}')
            else:
                nav_list.append({
                    'code': code,
                    'name': fund['fund_name'],
                    'type': fund['fund_type'],
                    'nav_date': None,
                    'unit_nav': None,
                    'accum_nav': None,
                    'daily_return': None
                })
                print('✗ 无数据')
        except Exception as e:
            print(f'✗ 错误: {str(e)[:30]}')
        
        time.sleep(0.3)
    
    # 显示结果表格
    print('\n' + '=' * 110)
    print('中航基金权益类基金最新净值列表')
    print('=' * 110)
    print(f'{"序号":<5} {"基金代码":<10} {"基金名称":<40} {"基金类型":<15} {"净值日期":<12} {"单位净值":<10} {"日涨跌":<8}')
    print('-' * 110)
    
    for i, item in enumerate(nav_list, 1):
        name = item['name'][:37] + '..' if len(item['name']) > 39 else item['name']
        fund_type = item['type'][:13] if len(item['type']) > 15 else item['type']
        nav_date = item['nav_date'] if item['nav_date'] else '--'
        unit_nav = f"{item['unit_nav']:.4f}" if item['unit_nav'] else '--'
        daily_return = f"{item['daily_return']:.2f}%" if item['daily_return'] else '--'
        
        print(f'{i:<5} {item["code"]:<10} {name:<40} {fund_type:<15} {nav_date:<12} {unit_nav:<10} {daily_return:<8}')
    
    print('=' * 110)
    print(f'\n总计: {len(nav_list)} 只基金')
    print(f'数据日期: {nav_list[0]["nav_date"] if nav_list and nav_list[0]["nav_date"] else "--"}')

if __name__ == '__main__':
    get_zh_nav_list()
