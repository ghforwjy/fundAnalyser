import sys
sys.path.insert(0, 'd:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')

print('=== 测试新鲜度机制 ===')

# 测试funddb模块导入
try:
    import funddb
    print('✓ funddb模块导入成功')
    print(f'  模块路径: {funddb.__file__}')
except Exception as e:
    print(f'✗ funddb模块导入失败: {e}')
    sys.exit(1)

# 测试update_holdings_meta函数
try:
    from funddb import update_holdings_meta
    print('✓ update_holdings_meta函数导入成功')
except Exception as e:
    print(f'✗ update_holdings_meta函数导入失败: {e}')
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
        cursor.execute('SELECT COUNT(*) FROM fund_info')
        count = cursor.fetchone()[0]
        print(f'  fund_info表记录数: {count}')
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
    sys.exit(1)

# 测试update_holdings_meta函数
try:
    print('\n=== 测试update_holdings_meta函数 ===')
    # 测试更新持仓元数据
    update_holdings_meta('000001', 'success')
    print('✓ update_holdings_meta函数调用成功')
    
    # 检查更新结果
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fund_data_meta WHERE table_name = ?', ('holdings_000001',))
        meta = cursor.fetchone()
        if meta:
            print(f'✓ 元数据更新成功')
            print(f'  最后同步时间: {meta[1]}')
            print(f'  同步状态: {meta[4]}')
        else:
            print('✗ 元数据未更新')
except Exception as e:
    print(f'✗ update_holdings_meta函数测试失败: {e}')
    import traceback
    traceback.print_exc()

# 测试新鲜度检查
try:
    print('\n=== 测试新鲜度检查 ===')
    # 测试当天是否已查询过
    from datetime import date
    today_str = date.today().strftime('%Y-%m-%d')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date(last_sync_time) as sync_date
            FROM fund_data_meta
            WHERE table_name = ?
        ''', ('holdings_000001',))
        meta = cursor.fetchone()
        
        if meta and meta[0] == today_str:
            print('✓ 新鲜度检查成功: 当天已查询过，不需要更新')
        else:
            print('✗ 新鲜度检查失败: 需要更新数据')
except Exception as e:
    print(f'✗ 新鲜度检查测试失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试完成 ===')
