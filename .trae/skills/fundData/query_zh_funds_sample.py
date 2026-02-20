"""
查询中航证券权益类基金最新净值 - 样本查询
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill
import time

def query_sample():
    skill = FundDataSkill()
    
    # 搜索中航证券的基金
    print('=== 中航证券权益类基金 ===')
    results = skill.search_funds('中航', 100)
    
    # 筛选权益类基金（股票型、混合型、指数型等）
    equity_types = ['股票', '混合', '指数']
    zh_funds = []
    for r in results:
        if '中航' in r['fund_name'] or '中航' in r['company_name']:
            if any(t in r['fund_type'] for t in equity_types):
                zh_funds.append(r)
    
    print(f'找到 {len(zh_funds)} 只中航证券权益类基金:')
    for f in zh_funds[:15]:
        print(f'  {f["fund_code"]} - {f["fund_name"]} ({f["fund_type"]})')
    
    if not zh_funds:
        print('未找到中航证券的权益类基金')
        return
    
    # 只获取前5只基金的净值作为示例
    sample_funds = zh_funds[:5]
    codes = [f['fund_code'] for f in sample_funds]
    
    print(f'\n准备同步前 {len(codes)} 只基金的最新净值作为示例...')
    
    # 逐个同步基金净值
    success_count = 0
    
    for i, code in enumerate(codes, 1):
        print(f'\n[{i}/{len(codes)}] 获取 {code} 的净值...')
        try:
            result = skill.sync_group_nav([code])
            if result['success']:
                success_count += 1
                print(f'  ✓ 成功')
            else:
                print(f'  ✗ 失败: {result["message"]}')
        except Exception as e:
            print(f'  ✗ 异常: {str(e)}')
        
        time.sleep(0.5)
    
    print(f'\n=== 同步完成: {success_count}/{len(codes)} 只基金 ===')
    
    # 查询最新净值
    print('\n=== 中航证券权益类基金最新净值 ===')
    print('-' * 80)
    print(f'{"基金代码":<10} {"基金名称":<35} {"净值日期":<12} {"单位净值":<10} {"日涨跌":<8}')
    print('-' * 80)
    
    for fund in sample_funds:
        code = fund['fund_code']
        nav_data = skill.query_fund_nav(code, limit=1)
        if nav_data:
            nav = nav_data[0]
            name = fund['fund_name'][:32] + '..' if len(fund['fund_name']) > 34 else fund['fund_name']
            nav_date = nav['nav_date'] if nav['nav_date'] else '--'
            unit_nav = f"{nav['unit_nav']:.4f}" if nav['unit_nav'] else '--'
            daily_return = f"{nav['daily_return']:.2f}%" if nav['daily_return'] else '--'
            print(f'{code:<10} {name:<35} {nav_date:<12} {unit_nav:<10} {daily_return:<8}')
        else:
            name = fund['fund_name'][:32] + '..' if len(fund['fund_name']) > 34 else fund['fund_name']
            print(f'{code:<10} {name:<35} {"--":<12} {"--":<10} {"--":<8}')
    
    print('-' * 80)
    print(f'\n注：共找到 {len(zh_funds)} 只中航证券权益类基金，以上为前 {len(sample_funds)} 只的示例数据')

if __name__ == '__main__':
    query_sample()
