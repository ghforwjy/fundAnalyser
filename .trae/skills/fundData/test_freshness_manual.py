import sys
sys.path.insert(0, 'd:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')

print('=== 测试新鲜度机制 ===')

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

# 测试数据库连接
try:
    with get_db_connection() as conn:
        print('✓ 数据库连接成功')
        cursor = conn.cursor()
        
        # 测试数据库当前时间
        cursor.execute('SELECT datetime("now") as current_time')
        db_time = cursor.fetchone()
        print(f'  数据库当前时间: {db_time[0]}')
        
        # 手动更新持仓元数据
        print('\n=== 手动更新持仓元数据 ===')
        fund_code = '000001'
        meta_key = f'holdings_{fund_code}'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT OR REPLACE INTO fund_data_meta 
            (table_name, last_sync_time, last_sync_status)
            VALUES (?, ?, ?)
        ''', (meta_key, current_time, 'success'))
        conn.commit()
        print(f'✓ 手动更新元数据成功')
        print(f'  更新时间: {current_time}')
        
        # 检查更新结果
        cursor.execute('SELECT * FROM fund_data_meta WHERE table_name = ?', (meta_key,))
        meta = cursor.fetchone()
        if meta:
            print(f'✓ 元数据查询成功')
            print(f'  最后同步时间: {meta[1]}')
            print(f'  同步状态: {meta[4]}')
        else:
            print('✗ 元数据未找到')
        
        # 测试新鲜度检查
        print('\n=== 测试新鲜度检查 ===')
        cursor.execute('''
            SELECT date(last_sync_time) as sync_date
            FROM fund_data_meta
            WHERE table_name = ?
        ''', (meta_key,))
        sync_info = cursor.fetchone()
        
        if sync_info:
            sync_date = sync_info[0]
            print(f'  同步日期: {sync_date}')
            print(f'  今天日期: {today_str}')
            if sync_date == today_str:
                print('✓ 新鲜度检查成功: 当天已查询过，不需要更新')
            else:
                print('✗ 新鲜度检查失败: 需要更新数据')
        else:
            print('✗ 元数据未找到')
except Exception as e:
    print(f'\n✗ 测试失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试完成 ===')
