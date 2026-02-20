import sys
sys.path.insert(0, 'd:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')

print('=== 测试组合数据查询新鲜度机制 ===')

# 测试当前系统时间
from datetime import datetime, date
print(f'当前系统时间: {datetime.now()}')
print(f'当前日期: {date.today()}')
today_str = date.today().strftime('%Y-%m-%d')
print(f'今天日期字符串: {today_str}')

# 测试funddb模块导入
try:
    import funddb
    print('\n✓ funddb模块导入成功')
    print(f'  模块路径: {funddb.__file__}')
except Exception as e:
    print(f'\n✗ funddb模块导入失败: {e}')
    sys.exit(1)

# 测试get_db_connection函数
try:
    from funddb import get_db_connection
    print('✓ get_db_connection函数导入成功')
except Exception as e:
    print(f'✗ get_db_connection函数导入失败: {e}')
    sys.exit(1)

# 测试组合数据查询
try:
    print('\n=== 测试组合数据查询 ===')
    from smart_fund_data import get_portfolio_funds_full
    print('✓ get_portfolio_funds_full函数导入成功')
    
    # 测试查询组合数据
    print('\n首次查询组合数据（应该触发同步）...')
    import time
    start_time = time.time()
    result = get_portfolio_funds_full(portfolio_id=2)
    end_time = time.time()
    
    print(f'✓ 组合数据查询成功')
    print(f'  查询耗时: {end_time - start_time:.2f} 秒')
    print(f'  组合ID: {result.get("portfolio_id")}')
    print(f'  组合名称: {result.get("portfolio_name")}')
    print(f'  基金数量: {result.get("fund_count")}')
    print(f'  新鲜度统计: {result.get("freshness_summary")}')
    
    # 测试第二次查询（应该使用缓存）
    print('\n第二次查询组合数据（应该使用缓存）...')
    start_time = time.time()
    result2 = get_portfolio_funds_full(portfolio_id=2)
    end_time = time.time()
    
    print(f'✓ 组合数据查询成功')
    print(f'  查询耗时: {end_time - start_time:.2f} 秒')
    print(f'  组合ID: {result2.get("portfolio_id")}')
    print(f'  组合名称: {result2.get("portfolio_name")}')
    print(f'  基金数量: {result2.get("fund_count")}')
    print(f'  新鲜度统计: {result2.get("freshness_summary")}')
    
    # 检查持仓数据新鲜度
    print('\n=== 检查持仓数据新鲜度 ===')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查第一只基金的持仓元数据
        if result.get('funds'):
            first_fund = result['funds'][0]
            fund_code = first_fund['fund_code']
            print(f'检查基金 {fund_code} 的持仓数据新鲜度...')
            
            cursor.execute('''
                SELECT date(last_sync_time) as sync_date
                FROM fund_data_meta
                WHERE table_name = ?
            ''', (f'holdings_{fund_code}',))
            meta = cursor.fetchone()
            
            if meta:
                sync_date = meta[0]
                print(f'  最后同步日期: {sync_date}')
                print(f'  今天日期: {today_str}')
                if sync_date == today_str:
                    print('✓ 持仓数据新鲜度检查成功: 当天已查询过')
                else:
                    print('✗ 持仓数据新鲜度检查失败: 需要更新')
            else:
                print('✗ 未找到持仓元数据')
except Exception as e:
    print(f'\n✗ 组合数据查询失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试完成 ===')
