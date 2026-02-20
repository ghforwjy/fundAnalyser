"""
查询中航证券权益类基金最新净值
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_data_skill import FundDataSkill
import time

def query_zh_funds():
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
    
    # 获取基金代码列表
    codes = [f['fund_code'] for f in zh_funds]
    print(f'\n准备同步 {len(codes)} 只基金的最新净值...')
    print('(使用单线程方式逐个获取，避免并发问题)')
    
    # 逐个同步基金净值
    success_count = 0
    total_records = 0
    
    for i, code in enumerate(codes, 1):
        print(f'\n[{i}/{len(codes)}] 获取 {code} 的净值...')
        try:
            result = skill.sync_group_nav([code])
            if result['success']:
                success_count += 1
                total_records += result['record_count']
                print(f'  ✓ 成功: {result["message"]}')
            else:
                print(f'  ✗ 失败: {result["message"]}')
        except Exception as e:
            print(f'  ✗ 异常: {str(e)}')
        
        # 添加延迟避免频率限制
        time.sleep(1)
    
    print(f'\n=== 同步完成 ===')
    print(f'成功: {success_count}/{len(codes)} 只基金')
    print(f'总记录数: {total_records} 条')
    
    # 查询最新净值
    print('\n=== 最新净值 ===')
    for fund in zh_funds[:10]:
        code = fund['fund_code']
        nav_data = skill.query_fund_nav(code, limit=1)
        if nav_data:
            nav = nav_data[0]
            print(f'{code} - {fund["fund_name"]}')
            print(f'  净值日期: {nav["nav_date"]}')
            print(f'  单位净值: {nav["unit_nav"]}')
            print(f'  累计净值: {nav["accum_nav"]}')
            if nav["daily_return"]:
                print(f'  日增长率: {nav["daily_return"]}%')
            print()

if __name__ == '__main__':
    query_zh_funds()
