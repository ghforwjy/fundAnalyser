import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2
fund_code = '000143'  # 鹏华双债加利债券A

print(f"=== 检查基金 {fund_code} 的导入数据 ===")

c.execute("""
    SELECT 
        fund_code,
        fund_name,
        shares,
        buy_nav,
        amount,
        current_value,
        profit_loss,
        profit_rate,
        cost_nav,
        import_source
    FROM portfolio_fund
    WHERE portfolio_id = ? AND fund_code = ?
""", (portfolio_id, fund_code))

row = c.fetchone()
if row:
    print(f"基金代码: {row['fund_code']}")
    print(f"基金名称: {row['fund_name']}")
    print(f"份额: {row['shares']}")
    print(f"买入净值: {row['buy_nav']}")
    print(f"amount: {row['amount']}")
    print(f"current_value: {row['current_value']}")
    print(f"profit_loss: {row['profit_loss']}")
    print(f"profit_rate: {row['profit_rate']}")
    print(f"cost_nav: {row['cost_nav']}")
    print(f"import_source: {row['import_source']}")
    
    # 验证计算
    if row['shares'] and row['buy_nav']:
        calc_cost = row['shares'] * row['buy_nav']
        print(f"\n验证: shares × buy_nav = {calc_cost:.2f}")
    
    if row['current_value'] and row['profit_loss']:
        calc_cost2 = row['current_value'] - row['profit_loss']
        print(f"验证: current_value - profit_loss = {calc_cost2:.2f}")
else:
    print("未找到数据")

conn.close()
