import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 检查持仓组合的 profit_loss 数据 ===")

# 获取所有基金的profit_loss
c.execute("""
    SELECT 
        fund_code,
        fund_name,
        shares,
        buy_nav,
        current_value,
        profit_loss
    FROM portfolio_fund
    WHERE portfolio_id = ?
    ORDER BY fund_code
""", (portfolio_id,))

rows = c.fetchall()

print(f"\n共 {len(rows)} 只基金\n")

print(f"{'基金代码':<10} {'基金名称':<30} {'current_value':<15} {'profit_loss':<15} {'状态':<10}")
print("-" * 90)

for row in rows:
    fund_code = row['fund_code']
    fund_name = row['fund_name'][:30]
    current_value = row['current_value']
    profit_loss = row['profit_loss']
    
    if profit_loss is None:
        status = "❌ NULL"
    else:
        status = "✅ 有值"
    
    print(f"{fund_code:<10} {fund_name:<30} {str(current_value):<15} {str(profit_loss):<15} {status:<10}")

conn.close()
