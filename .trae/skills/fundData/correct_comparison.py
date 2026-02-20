import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 正确的盈亏比较 ===")
print("规则：有profit_loss的用profit_loss，没有的用 shares * latest_nav - amount 计算")

# 获取数据库中的所有基金
c.execute("""
    SELECT 
        pf.fund_code,
        pf.fund_name,
        pf.shares,
        pf.buy_nav,
        pf.amount,
        pf.current_value,
        pf.profit_loss,
        fn.unit_nav as latest_nav
    FROM portfolio_fund pf
    LEFT JOIN (
        SELECT fund_code, unit_nav
        FROM fund_nav
        WHERE (fund_code, nav_date) IN (
            SELECT fund_code, MAX(nav_date)
            FROM fund_nav
            GROUP BY fund_code
        )
    ) fn ON pf.fund_code = fn.fund_code
    WHERE pf.portfolio_id = ?
""", (portfolio_id,))

db_funds = {row['fund_code']: row for row in c.fetchall()}

# 原始图片中的基金数据
image_funds = {
    '024389': {'profit': 4688.38},
    '022853': {'profit': 4103.50},
    '021489': {'profit': 2764.70},
    '021492': {'profit': 2615.24},
    '024291': {'profit': 0.03},
    '024290': {'profit': 0.04},
    '001052': {'profit': 9797.49},
    '486001': {'profit': 18577.96},
    '001595': {'profit': 30024.79},
    '000143': {'profit': 90596.94},
    '006331': {'profit': 1449.00},
    '018957': {'profit': 16456.71},
    '007994': {'profit': 94469.69},
    '501022': {'profit': 29704.78},
    '160514': {'profit': 14807.42},
    '009424': {'profit': 11674.48},
    '013431': {'profit': 17730.12},
    '004011': {'profit': 7521.17},
}

print(f"\n{'基金代码':<10} {'基金名称':<30} {'数据库盈亏':<12} {'图片盈亏':<12} {'差异':<12} {'状态':<10}")
print("-" * 100)

total_db_profit = 0
total_image_profit = 0

for fund_code in sorted(set(db_funds.keys()) & set(image_funds.keys())):
    db_fund = db_funds[fund_code]
    img_fund = image_funds[fund_code]
    
    # 计算数据库盈亏：优先使用profit_loss，如果没有则计算
    if db_fund['profit_loss'] is not None:
        db_profit = db_fund['profit_loss']
    else:
        shares = db_fund['shares'] or 0
        latest_nav = db_fund['latest_nav'] or 0
        amount = db_fund['amount'] or 0
        db_profit = shares * latest_nav - amount
    
    img_profit = img_fund['profit']
    
    total_db_profit += db_profit
    total_image_profit += img_profit
    
    diff = db_profit - img_profit
    status = "✅ 匹配" if abs(diff) < 1 else "⚠️ 差异"
    
    print(f"{fund_code:<10} {db_fund['fund_name'][:30]:<30} {db_profit:<12.2f} {img_profit:<12.2f} {diff:<12.2f} {status:<10}")

print("-" * 100)
print(f"\n{'总计':<40} {total_db_profit:<12.2f} {total_image_profit:<12.2f} {total_db_profit - total_image_profit:<12.2f}")

print(f"\n=== 汇总对比 ===")
print(f"数据库总盈亏: {total_db_profit:.2f}")
print(f"图片总盈亏: {total_image_profit:.2f}")
print(f"盈亏差异: {total_db_profit - total_image_profit:.2f}")

conn.close()
