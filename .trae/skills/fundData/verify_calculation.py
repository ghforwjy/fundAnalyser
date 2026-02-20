import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 验证计算：成本净值 × 份额 - 当前市值 = 盈亏 ===")
print("\n公式：cost_nav × shares - current_value = profit_loss")
print("或者：buy_nav × shares - current_value = profit_loss")
print()

# 获取所有基金数据
c.execute("""
    SELECT 
        fund_code,
        fund_name,
        shares,
        buy_nav,
        cost_nav,
        current_value,
        profit_loss
    FROM portfolio_fund
    WHERE portfolio_id = ? AND profit_loss IS NOT NULL
""", (portfolio_id,))

rows = c.fetchall()

print(f"{'基金代码':<10} {'基金名称':<30} {'验证结果':<15} {'差异':<10}")
print("-" * 80)

for row in rows:
    fund_code = row['fund_code']
    fund_name = row['fund_name'][:30]
    shares = row['shares'] or 0
    buy_nav = row['buy_nav'] or 0
    cost_nav = row['cost_nav'] or 0
    current_value = row['current_value'] or 0
    profit_loss = row['profit_loss'] or 0
    
    # 使用 buy_nav 计算
    calc_profit_buy = buy_nav * shares - current_value
    diff_buy = calc_profit_buy - profit_loss
    
    # 使用 cost_nav 计算（如果有）
    if cost_nav:
        calc_profit_cost = cost_nav * shares - current_value
        diff_cost = calc_profit_cost - profit_loss
    else:
        calc_profit_cost = None
        diff_cost = None
    
    # 判断哪个更准确
    if diff_cost is not None and abs(diff_cost) < abs(diff_buy):
        result = "cost_nav 准确"
        diff = diff_cost
    else:
        result = "buy_nav 准确"
        diff = diff_buy
    
    match = "✅ 匹配" if abs(diff) < 0.01 else "❌ 不匹配"
    
    print(f"{fund_code:<10} {fund_name:<30} {result:<15} {diff:<10.2f} {match}")
    
    # 详细数据
    cost_nav_str = f"{cost_nav:.4f}" if cost_nav else "N/A"
    print(f"  份额: {shares:.2f}, buy_nav: {buy_nav:.4f}, cost_nav: {cost_nav_str}")
    print(f"  当前市值: {current_value:.2f}, 盈亏: {profit_loss:.2f}")
    print(f"  buy_nav计算: {buy_nav:.4f} × {shares:.2f} - {current_value:.2f} = {calc_profit_buy:.2f}")
    if calc_profit_cost is not None:
        print(f"  cost_nav计算: {cost_nav:.4f} × {shares:.2f} - {current_value:.2f} = {calc_profit_cost:.2f}")
    print()

conn.close()
