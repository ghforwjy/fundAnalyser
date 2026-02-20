import sqlite3

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2  # 持仓组合

# 有差异的4只基金代码
diff_funds = ['022853', '021489', '021492', '024389']

print("=== 4只差异基金详细分析 ===")

# 获取数据库中的数据
c.execute("""
    SELECT 
        pf.fund_code,
        pf.fund_name,
        pf.shares,
        pf.buy_nav,
        pf.amount,
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
    WHERE pf.portfolio_id = ? AND pf.fund_code IN (?, ?, ?, ?)
""", (portfolio_id, *diff_funds))

db_funds = {row['fund_code']: row for row in c.fetchall()}

# 图片中的数据（从原始图提取）
image_funds = {
    '022853': {'shares': 7675.50, 'buy_nav': 1.1335, 'latest_nav': 1.6681, 'amount': 8700.00},
    '021489': {'shares': 2525.91, 'buy_nav': 1.7499, 'latest_nav': 2.8444, 'amount': 4420.00},
    '021492': {'shares': 8614.15, 'buy_nav': 1.0324, 'latest_nav': 1.3360, 'amount': 8893.26},
    '024389': {'shares': 10020.04, 'buy_nav': 0.5988, 'latest_nav': 1.0667, 'amount': 6000.00},
}

print(f"\n{'基金代码':<10} {'字段':<15} {'数据库值':<15} {'图片值':<15} {'差异':<15} {'说明':<20}")
print("-" * 120)

for fund_code in diff_funds:
    db_fund = db_funds.get(fund_code)
    img_fund = image_funds.get(fund_code)
    
    if not db_fund or not img_fund:
        continue
    
    fund_name = db_fund['fund_name'][:20]
    
    # 份额对比
    db_shares = db_fund['shares'] or 0
    img_shares = img_fund['shares']
    shares_diff = db_shares - img_shares
    shares_match = abs(shares_diff) < 0.01
    
    print(f"{fund_code:<10} {'份额':<15} {db_shares:<15.4f} {img_shares:<15.4f} {shares_diff:<15.4f} {'✅ 匹配' if shares_match else '❌ 不匹配':<20}")
    
    # 买入净值对比
    db_buy_nav = db_fund['buy_nav'] or 0
    img_buy_nav = img_fund['buy_nav']
    buy_nav_diff = db_buy_nav - img_buy_nav
    buy_nav_match = abs(buy_nav_diff) < 0.0001
    
    print(f"{'':<10} {'买入净值':<15} {db_buy_nav:<15.4f} {img_buy_nav:<15.4f} {buy_nav_diff:<15.4f} {'✅ 匹配' if buy_nav_match else '❌ 不匹配':<20}")
    
    # 最新净值对比
    db_latest_nav = db_fund['latest_nav'] or 0
    img_latest_nav = img_fund['latest_nav']
    latest_nav_diff = db_latest_nav - img_latest_nav
    latest_nav_match = abs(latest_nav_diff) < 0.0001
    
    print(f"{'':<10} {'最新净值':<15} {db_latest_nav:<15.4f} {img_latest_nav:<15.4f} {latest_nav_diff:<15.4f} {'✅ 匹配' if latest_nav_match else '❌ 不匹配':<20}")
    
    # 成本对比
    db_amount = db_fund['amount'] or 0
    img_amount = img_fund['amount']
    amount_diff = db_amount - img_amount
    amount_match = abs(amount_diff) < 0.01
    
    print(f"{'':<10} {'成本':<15} {db_amount:<15.2f} {img_amount:<15.2f} {amount_diff:<15.2f} {'✅ 匹配' if amount_match else '❌ 不匹配':<20}")
    
    # 计算盈亏
    db_profit = db_shares * db_latest_nav - db_amount
    img_profit = img_shares * img_latest_nav - img_amount
    profit_diff = db_profit - img_profit
    
    print(f"{'':<10} {'计算盈亏':<15} {db_profit:<15.2f} {img_profit:<15.2f} {profit_diff:<15.2f} {'':<20}")
    
    print(f"{'':<10} {'基金名称':<15} {fund_name:<50}")
    print("-" * 120)

print("\n=== 差异原因总结 ===")
for fund_code in diff_funds:
    db_fund = db_funds.get(fund_code)
    img_fund = image_funds.get(fund_code)
    
    if not db_fund or not img_fund:
        continue
    
    fund_name = db_fund['fund_name']
    
    db_shares = db_fund['shares'] or 0
    img_shares = img_fund['shares']
    
    db_latest_nav = db_fund['latest_nav'] or 0
    img_latest_nav = img_fund['latest_nav']
    
    db_amount = db_fund['amount'] or 0
    img_amount = img_fund['amount']
    
    print(f"\n{fund_code} - {fund_name}:")
    
    if abs(db_shares - img_shares) > 0.01:
        print(f"  ❌ 份额不一致: 数据库={db_shares:.2f}, 图片={img_shares:.2f}")
    else:
        print(f"  ✅ 份额一致: {db_shares:.2f}")
    
    if abs(db_latest_nav - img_latest_nav) > 0.0001:
        print(f"  ❌ 最新净值不一致: 数据库={db_latest_nav:.4f}, 图片={img_latest_nav:.4f}")
    else:
        print(f"  ✅ 最新净值一致: {db_latest_nav:.4f}")
    
    if abs(db_amount - img_amount) > 0.01:
        print(f"  ❌ 成本不一致: 数据库={db_amount:.2f}, 图片={img_amount:.2f}")
    else:
        print(f"  ✅ 成本一致: {db_amount:.2f}")
    
    db_profit = db_shares * db_latest_nav - db_amount
    img_profit = img_shares * img_latest_nav - img_amount
    print(f"  📊 盈亏差异: {db_profit - img_profit:.2f}")

conn.close()
