import sys
sys.path.insert(0, 'd:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')

print('=== 测试funddb模块导入 ===')

# 测试funddb模块导入
try:
    import funddb
    print('✓ funddb模块导入成功')
    print(f'  模块路径: {funddb.__file__}')
except Exception as e:
    print(f'✗ funddb模块导入失败: {e}')

# 测试update_holdings_meta函数
try:
    from funddb import update_holdings_meta
    print('✓ update_holdings_meta函数导入成功')
except Exception as e:
    print(f'✗ update_holdings_meta函数导入失败: {e}')

# 测试get_db_connection函数
try:
    from funddb import get_db_connection
    print('✓ get_db_connection函数导入成功')
except Exception as e:
    print(f'✗ get_db_connection函数导入失败: {e}')

# 测试update_sync_meta函数
try:
    from funddb import update_sync_meta
    print('✓ update_sync_meta函数导入成功')
except Exception as e:
    print(f'✗ update_sync_meta函数导入失败: {e}')

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

# 测试组合查询
try:
    from smart_fund_data import get_portfolio_funds_full
    print('✓ get_portfolio_funds_full函数导入成功')
    
    # 测试查询组合数据
    result = get_portfolio_funds_full(portfolio_id=2)
    print(f'✓ 组合数据查询成功')
    print(f'  组合ID: {result.get("portfolio_id")}')
    print(f'  组合名称: {result.get("portfolio_name")}')
    print(f'  基金数量: {result.get("fund_count")}')
    print(f'  新鲜度统计: {result.get("freshness_summary")}')
except Exception as e:
    print(f'✗ 组合查询失败: {e}')
    import traceback
    traceback.print_exc()

print('\n=== 测试完成 ===')
