import sys
sys.path.append('d:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')
from database import get_db_connection
import datetime

print('=== 检查持仓数据同步状态 ===')

# 检查fund_data_meta表中持仓相关的记录
with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # 查询所有持仓相关的记录
    cursor.execute('''
        SELECT * FROM fund_data_meta 
        WHERE table_name LIKE 'holdings_%'
        ORDER BY last_sync_time DESC
        LIMIT 10
    ''')
    
    rows = cursor.fetchall()
    print(f'\nfund_data_meta表中持仓相关记录（前10条）:')
    print(f'记录数量: {len(rows)}')
    
    for row in rows:
        table_name = row[0]
        last_sync_time = row[1]
        record_count = row[2]
        last_sync_status = row[3]
        last_error = row[4]
        
        fund_code = table_name.replace('holdings_', '')
        sync_date = last_sync_time.split(' ')[0] if last_sync_time else 'N/A'
        
        print(f'\n基金: {fund_code}')
        print(f'  同步时间: {last_sync_time}')
        print(f'  同步日期: {sync_date}')
        print(f'  记录数量: {record_count}')
        print(f'  同步状态: {last_sync_status}')
        print(f'  错误信息: {last_error}')

# 检查今天的日期
print(f'\n=== 系统日期信息 ===')
print(f'今天日期: {datetime.date.today()}')
print(f'当前时间: {datetime.datetime.now()}')

# 检查持仓数据同步的具体逻辑
print('\n=== 持仓数据同步逻辑分析 ===')
print('1. 持仓数据是什么？')
print('   - 持仓数据是指基金持有的股票、债券等资产的详细信息')
print('   - 包括股票代码、股票名称、持仓市值、持仓比例、报告期等')
print('   - 数据来源：AKShare的fund_portfolio_hold_em接口')
print('   - 存储表：fund_stock_holding')

print('\n2. 为什么同步日期是2月16日？')
print('   - 检查get_fund_holdings函数的新鲜度判断逻辑')
print('   - 逻辑：检查fund_data_meta表的last_sync_time字段')
print('   - 条件：如果当天（按日期）没有查询过，就触发更新')
print('   - 原因：可能是update_holdings_meta函数未正确更新时间戳')

print('\n3. 检查update_holdings_meta函数的实现')
print('   - 搜索整个代码库，寻找update_holdings_meta函数')
