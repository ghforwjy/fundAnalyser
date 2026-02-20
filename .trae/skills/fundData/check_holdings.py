from database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    print('='*60)
    print('持仓数据表检查')
    print('='*60)
    
    # 股票持仓
    cursor.execute('SELECT COUNT(*) as count FROM fund_stock_holding')
    stock_count = cursor.fetchone()['count']
    print(f'股票持仓记录数: {stock_count}')
    
    if stock_count > 0:
        cursor.execute('SELECT DISTINCT fund_code FROM fund_stock_holding')
        funds = cursor.fetchall()
        print(f'涉及基金数: {len(funds)}')
        
        cursor.execute('SELECT DISTINCT quarter FROM fund_stock_holding ORDER BY quarter DESC LIMIT 10')
        quarters = cursor.fetchall()
        print(f'报告期: {[q["quarter"] for q in quarters]}')
    
    # 债券持仓
    cursor.execute('SELECT COUNT(*) as count FROM fund_bond_holding')
    bond_count = cursor.fetchone()['count']
    print(f'\n债券持仓记录数: {bond_count}')
    
    # 行业配置
    cursor.execute('SELECT COUNT(*) as count FROM fund_industry_allocation')
    industry_count = cursor.fetchone()['count']
    print(f'行业配置记录数: {industry_count}')
    
    # 检查数据库位置
    cursor.execute("SELECT file FROM pragma_database_list WHERE name='main'")
    db_path = cursor.fetchone()
    print(f'\n数据库位置: {db_path["file"] if db_path else "未知"}')
