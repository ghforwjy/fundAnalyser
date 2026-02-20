from database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # 查询持仓历史记录
    cursor.execute('''
        SELECT fund_code, record_date, shares, nav, market_value, shares_change
        FROM holding_history
        WHERE portfolio_id = 2
        ORDER BY fund_code, record_date DESC
    ''')
    rows = cursor.fetchall()
    
    print(f"持仓历史记录数: {len(rows)}\n")
    print(f"{'基金代码':<10} {'记录日期':<12} {'份额':>12} {'净值':>8} {'市值':>14} {'份额变动':>10}")
    print("-" * 80)
    
    for row in rows:
        code = row['fund_code']
        date = row['record_date']
        shares = row['shares'] or 0
        nav = row['nav'] or 0
        mv = row['market_value'] or 0
        change = row['shares_change']
        change_str = f"{change:+.2f}" if change else "-"
        print(f"{code:<10} {date:<12} {shares:>12.2f} {nav:>8.4f} {mv:>14.2f} {change_str:>10}")
    
    if not rows:
        print("\n没有持仓历史记录！")
        print("\n需要使用 record_holding() 函数记录持仓快照才能计算盈亏。")
