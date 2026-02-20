import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
c = conn.cursor()

print("=== 检查 portfolio_fund 表结构 ===")

# 获取表结构
c.execute("PRAGMA table_info(portfolio_fund)")
columns = c.fetchall()

print("\n表字段:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 检查是否有 cost_nav 字段
cost_nav_col = [col for col in columns if col[1] == 'cost_nav']
if cost_nav_col:
    print("\n✅ cost_nav 字段存在")
else:
    print("\n❌ cost_nav 字段不存在")

# 检查所有基金的 cost_nav 数据
print("\n=== 检查所有基金的 cost_nav 数据 ===")
c.execute("""
    SELECT fund_code, fund_name, buy_nav, cost_nav, amount, current_value, profit_loss
    FROM portfolio_fund
    WHERE portfolio_id = 2
""")

rows = c.fetchall()
for row in rows:
    fund_code = row[0]
    fund_name = row[1]
    buy_nav = row[2]
    cost_nav = row[3]
    amount = row[4]
    current_value = row[5]
    profit_loss = row[6]
    
    print(f"\n{fund_code}: {fund_name[:30]}")
    print(f"  buy_nav: {buy_nav}")
    print(f"  cost_nav: {cost_nav}")
    print(f"  amount: {amount}")
    print(f"  current_value: {current_value}")
    print(f"  profit_loss: {profit_loss}")
    
    # 验证 cost_nav 计算
    if current_value and profit_loss and amount:
        calc_cost_nav = (current_value - profit_loss) / (amount / buy_nav) if buy_nav and amount else 0
        print(f"  验证 cost_nav: {calc_cost_nav:.4f}")

conn.close()
