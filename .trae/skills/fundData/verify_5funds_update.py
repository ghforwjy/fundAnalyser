import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

# 检查这5只基金的更新后的数据
fund_codes = ['001052', '001595', '007994', '024290', '486001']

print("=== 验证5只基金更新后的盈亏数据 ===")

for fund_code in fund_codes:
    c.execute("""
        SELECT 
            fund_code,
            fund_name,
            shares,
            buy_nav,
            amount,
            current_value,
            profit_loss,
            update_time
        FROM portfolio_fund
        WHERE portfolio_id = ? AND fund_code = ?
    """, (portfolio_id, fund_code))
    
    row = c.fetchone()
    if row:
        print(f"\n基金代码: {row['fund_code']}")
        print(f"基金名称: {row['fund_name']}")
        print(f"份额: {row['shares']}")
        print(f"买入净值: {row['buy_nav']}")
        print(f"成本: {row['amount']}")
        print(f"当前市值: {row['current_value']}")
        print(f"盈亏: {row['profit_loss']}")
        print(f"更新时间: {row['update_time']}")
        
        # 验证盈亏计算
        if row['current_value'] and row['amount']:
            calc_profit = row['current_value'] - row['amount']
            print(f"验证: {row['current_value']} - {row['amount']} = {calc_profit:.2f}")
    else:
        print(f"\n❌ 基金 {fund_code} 未找到")

conn.close()
