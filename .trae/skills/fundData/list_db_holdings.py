import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 持仓组合（ID: 2）当前数据 ===")

# 获取所有基金数据
c.execute("""
    SELECT 
        pf.fund_code,
        pf.fund_name,
        pf.shares,
        pf.buy_nav,
        pf.amount,
        pf.current_value,
        pf.profit_loss,
        fn.unit_nav as latest_nav,
        fn.nav_date
    FROM portfolio_fund pf
    LEFT JOIN (
        SELECT fund_code, unit_nav, nav_date
        FROM fund_nav
        WHERE (fund_code, nav_date) IN (
            SELECT fund_code, MAX(nav_date)
            FROM fund_nav
            GROUP BY fund_code
        )
    ) fn ON pf.fund_code = fn.fund_code
    WHERE pf.portfolio_id = ?
    ORDER BY pf.fund_code
""", (portfolio_id,))

rows = c.fetchall()

print(f"\n共 {len(rows)} 只基金\n")

print(f"{'基金代码':<10} {'基金名称':<35} {'份额':<12} {'买入净值':<10} {'成本':<12} {'最新净值':<10} {'市值':<12} {'盈亏':<12}")
print("-" * 130)

total_cost = 0
total_market_value = 0
total_profit = 0

for row in rows:
    fund_code = row['fund_code']
    fund_name = row['fund_name']
    shares = row['shares'] or 0
    buy_nav = row['buy_nav'] or 0
    amount = row['amount'] or 0
    latest_nav = row['latest_nav'] or 0
    
    # 计算市值
    market_value = shares * latest_nav
    
    # 计算盈亏：优先使用profit_loss，如果没有则计算
    if row['profit_loss'] is not None:
        profit = row['profit_loss']
    else:
        profit = market_value - amount
    
    total_cost += amount
    total_market_value += market_value
    total_profit += profit
    
    print(f"{fund_code:<10} {fund_name[:35]:<35} {shares:<12.2f} {buy_nav:<10.4f} {amount:<12.2f} {latest_nav:<10.4f} {market_value:<12.2f} {profit:<12.2f}")

print("-" * 130)
print(f"{'总计':<45} {total_cost:<12.2f} {'':<10} {total_market_value:<12.2f} {total_profit:<12.2f}")

print(f"\n=== 汇总 ===")
print(f"总成本: {total_cost:.2f}")
print(f"总市值: {total_market_value:.2f}")
print(f"总盈亏: {total_profit:.2f}")
print(f"收益率: {(total_profit/total_cost*100) if total_cost > 0 else 0:.2f}%")

conn.close()
