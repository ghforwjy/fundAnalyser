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

# 检查是否有 profit_loss 字段
profit_loss_col = [col for col in columns if col[1] == 'profit_loss']
if profit_loss_col:
    print("\n✅ profit_loss 字段存在")
else:
    print("\n❌ profit_loss 字段不存在")

# 检查所有基金的数据
print("\n=== 检查所有基金的 profit_loss 数据 ===")
c.execute("""
    SELECT fund_code, fund_name, profit_loss, current_value, amount
    FROM portfolio_fund
    WHERE portfolio_id = 2
""")

rows = c.fetchall()
for row in rows:
    fund_code = row[0]
    fund_name = row[1]
    profit_loss = row[2]
    current_value = row[3]
    amount = row[4]
    
    # 计算理论盈亏
    if current_value and amount:
        calc_profit = current_value - amount
    else:
        calc_profit = 0
    
    print(f"{fund_code}: {fund_name[:30]}")
    print(f"  profit_loss: {profit_loss}")
    print(f"  current_value: {current_value}")
    print(f"  amount: {amount}")
    print(f"  计算盈亏: {calc_profit:.2f}")
    print()

conn.close()
