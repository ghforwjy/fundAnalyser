import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 最终对比：更新后的数据库 vs 原始图片 ===")

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

# 原始图片中的基金数据（从图1和图2提取）
image_funds = {
    # 图1数据
    '024389': {'name': '中航智选领航混合C', 'market_value': 10688.38, 'profit': 4688.38},
    '022853': {'name': '中航优选领航混合C', 'market_value': 12803.50, 'profit': 4103.50},
    '021489': {'name': '中航趋势领航混合A', 'market_value': 7184.70, 'profit': 2764.70},
    '021492': {'name': '中航远见领航混合C', 'market_value': 11508.50, 'profit': 2615.24},
    '024291': {'name': '中航月月鑫30天持有期债券C', 'market_value': 10.03, 'profit': 0.03},
    '024290': {'name': '中航月月鑫30天持有期债券A', 'market_value': 10.04, 'profit': 0.04},
    '001052': {'name': '华夏中证500ETF联接A', 'market_value': 18297.49, 'profit': 9797.49},
    '486001': {'name': '工银全球股票(QDII)人民币', 'market_value': 32979.62, 'profit': 18577.96},
    '001595': {'name': '天弘中证银行ETF联接C', 'market_value': 63524.79, 'profit': 30024.79},
    '000143': {'name': '鹏华双债加利债券A', 'market_value': 388704.74, 'profit': 90596.94},
    '006331': {'name': '中银国有企业债C', 'market_value': 31449.00, 'profit': 1449.00},
    '018957': {'name': '中航机遇领航混合发起C', 'market_value': 25956.71, 'profit': 16456.71},
    # 图2数据
    '007994': {'name': '华夏中证500指数增强A', 'market_value': 259469.63, 'profit': 94469.69},
    '501022': {'name': '银华鑫盛灵活配置混合(LOF)A', 'market_value': 202204.78, 'profit': 29704.78},
    '160514': {'name': '博时稳健回报债券(LOF)C', 'market_value': 114807.42, 'profit': 14807.42},
    '009424': {'name': '招商瑞信稳健配置混合C', 'market_value': 111674.48, 'profit': 11674.48},
    '013431': {'name': '华泰柏瑞景气汇选三年持有期混合A', 'market_value': 67730.12, 'profit': 17730.12},
    '004011': {'name': '华泰柏瑞鼎利灵活配置混合C', 'market_value': 52567.55, 'profit': 7521.17},
}

print(f"\n{'基金代码':<10} {'基金名称':<30} {'数据库盈亏':<12} {'图片盈亏':<12} {'差异':<12} {'状态':<10}")
print("-" * 100)

total_db_profit = 0
total_image_profit = 0

# 先显示匹配的基金
for fund_code in sorted(set(db_funds.keys()) & set(image_funds.keys())):
    db_fund = db_funds[fund_code]
    img_fund = image_funds[fund_code]
    
    db_profit = db_fund['profit_loss'] or 0
    img_profit = img_fund['profit']
    
    total_db_profit += db_profit
    total_image_profit += img_profit
    
    diff = db_profit - img_profit
    status = "✅ 匹配" if abs(diff) < 1 else "⚠️ 差异"
    
    print(f"{fund_code:<10} {db_fund['fund_name'][:30]:<30} {db_profit:<12.2f} {img_profit:<12.2f} {diff:<12.2f} {status:<10}")

print("-" * 100)

# 显示数据库中有但图片中没有的基金
print("\n=== 数据库中有但图片中没有的基金 ===")
for fund_code in sorted(set(db_funds.keys()) - set(image_funds.keys())):
    db_fund = db_funds[fund_code]
    db_profit = db_fund['profit_loss'] or 0
    total_db_profit += db_profit
    
    print(f"{fund_code:<10} {db_fund['fund_name'][:30]:<30} {db_profit:<12.2f} {'N/A':<12} {'N/A':<12} ❌ 未匹配")

# 显示图片中有但数据库中没有的基金
print("\n=== 图片中有但数据库中没有的基金 ===")
for fund_code in sorted(set(image_funds.keys()) - set(db_funds.keys())):
    img_fund = image_funds[fund_code]
    img_profit = img_fund['profit']
    total_image_profit += img_profit
    
    print(f"{fund_code:<10} {img_fund['name'][:30]:<30} {'N/A':<12} {img_profit:<12.2f} {'N/A':<12} ❌ 未匹配")

print("-" * 100)
print(f"\n{'总计':<40} {total_db_profit:<12.2f} {total_image_profit:<12.2f} {total_db_profit - total_image_profit:<12.2f}")

print(f"\n=== 汇总对比 ===")
print(f"数据库总盈亏: {total_db_profit:.2f}")
print(f"图片总盈亏: {total_image_profit:.2f}")
print(f"盈亏差异: {total_db_profit - total_image_profit:.2f}")
print(f"差异百分比: {(total_db_profit - total_image_profit)/total_image_profit*100 if total_image_profit > 0 else 0:.2f}%")

conn.close()
