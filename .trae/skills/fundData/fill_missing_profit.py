import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

# 需要填充盈亏的9只基金
funds_to_fill = [
    '000143', '004011', '006331', '009424', '013431', 
    '018957', '024291', '160514', '501022'
]

print("=== 为9只基金填充盈亏数据 ===\n")

for fund_code in funds_to_fill:
    # 获取基金数据
    c.execute("""
        SELECT fund_code, fund_name, shares, buy_nav
        FROM portfolio_fund
        WHERE portfolio_id = ? AND fund_code = ?
    """, (portfolio_id, fund_code))
    
    row = c.fetchone()
    if not row:
        print(f"❌ {fund_code}: 未找到基金数据")
        continue
    
    shares = row['shares'] or 0
    buy_nav = row['buy_nav'] or 0
    
    # 获取最新净值
    c.execute("""
        SELECT unit_nav, nav_date
        FROM fund_nav
        WHERE fund_code = ?
        ORDER BY nav_date DESC
        LIMIT 1
    """, (fund_code,))
    
    nav_row = c.fetchone()
    if not nav_row:
        print(f"❌ {fund_code}: 未找到净值数据")
        continue
    
    latest_nav = nav_row['unit_nav'] or 0
    nav_date = nav_row['nav_date']
    
    # 计算
    cost = shares * buy_nav  # 成本
    market_value = shares * latest_nav  # 市值
    profit_loss = market_value - cost  # 盈亏
    profit_rate = profit_loss / cost if cost > 0 else 0  # 收益率
    
    print(f"{fund_code}: {row['fund_name'][:30]}")
    print(f"  份额: {shares:.2f}, 买入净值: {buy_nav:.4f}, 最新净值: {latest_nav:.4f}")
    print(f"  成本: {cost:.2f}, 市值: {market_value:.2f}")
    print(f"  盈亏: {profit_loss:.2f}, 收益率: {profit_rate*100:.2f}%")
    
    # 更新数据库
    c.execute("""
        UPDATE portfolio_fund SET
            current_value = ?,
            profit_loss = ?,
            profit_rate = ?,
            cost_nav = ?,
            import_source = 'calculated',
            import_date = DATE('now'),
            update_time = CURRENT_TIMESTAMP
        WHERE portfolio_id = ? AND fund_code = ?
    """, (market_value, profit_loss, profit_rate, buy_nav, portfolio_id, fund_code))
    
    if c.rowcount > 0:
        print(f"  ✅ 已更新\n")
    else:
        print(f"  ❌ 更新失败\n")

conn.commit()
conn.close()

print("=== 完成 ===")
