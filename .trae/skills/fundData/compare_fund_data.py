import sqlite3

# 连接fundData skill的数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2  # 持仓组合

print("=== 逐只基金数据对比分析 ===")

# 获取当前数据库中的基金数据
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
    WHERE pf.portfolio_id = ?
""", (portfolio_id,))

db_funds = c.fetchall()

# 图片中的基金数据（从原始图提取）
image_funds = {
    # 图1数据
    '024389': {'name': '中航智选领航混合C', 'amount': 0, 'profit': 0},  # 需要具体数据
    '022853': {'name': '中航优选领航混合C', 'amount': 0, 'profit': 0},
    '021489': {'name': '中航趋势领航混合A', 'amount': 0, 'profit': 0},
    '021492': {'name': '中航远见领航混合C', 'amount': 0, 'profit': 0},
    '024291': {'name': '中航月月鑫30天持有期债券C', 'amount': 10.03, 'profit': 0.03},
    '024290': {'name': '中航月月鑫30天持有期债券A', 'amount': 10.04, 'profit': 0.04},
    '001052': {'name': '华夏中证500ETF联接A', 'amount': 18297.49, 'profit': 9797.49},
    '486001': {'name': '工银全球股票(QDII)人民币', 'amount': 32979.62, 'profit': 18577.96},
    '001595': {'name': '天弘中证银行ETF联接C', 'amount': 63524.79, 'profit': 30024.79},
    '000143': {'name': '鹏华双债加利债券A', 'amount': 388704.74, 'profit': 90596.94},
    '006331': {'name': '中银国有企业债C', 'amount': 31449.00, 'profit': 1449.00},
    '018957': {'name': '中航机遇领航混合发起C', 'amount': 25956.71, 'profit': 16456.71},
    # 图2数据
    '007994': {'name': '华夏中证500指数增强A', 'amount': 259469.63, 'profit': 94469.69},
    '501022': {'name': '银华鑫盛灵活配置混合(LOF)A', 'amount': 202204.78, 'profit': 29704.78},
    '160514': {'name': '博时稳健回报债券(LOF)C', 'amount': 114807.42, 'profit': 14807.42},
    '009424': {'name': '招商瑞信稳健配置混合C', 'amount': 111674.48, 'profit': 11674.48},
    '013431': {'name': '华泰柏瑞景气汇选三年持有期混合A', 'amount': 67730.12, 'profit': 17730.12},
    '004011': {'name': '华泰柏瑞鼎利灵活配置混合C', 'amount': 52567.55, 'profit': 7521.17},
}

print(f"\n{'基金代码':<10} {'基金名称':<30} {'数据库市值':<12} {'图片市值':<12} {'差异':<12} {'状态':<10}")
print("-" * 100)

total_db_market_value = 0
total_db_cost = 0
total_db_profit = 0
total_image_profit = 0

for fund in db_funds:
    fund_code = fund['fund_code']
    fund_name = fund['fund_name']
    shares = fund['shares'] or 0
    buy_nav = fund['buy_nav'] or 0
    amount = fund['amount'] or 0
    latest_nav = fund['latest_nav'] or 0
    
    # 计算成本
    if amount > 0:
        cost = amount
    elif shares > 0 and buy_nav > 0:
        cost = shares * buy_nav
    else:
        cost = 0
    
    # 计算市值和盈亏
    market_value = shares * latest_nav
    profit = market_value - cost
    
    total_db_market_value += market_value
    total_db_cost += cost
    total_db_profit += profit
    
    # 检查是否在图片中
    if fund_code in image_funds:
        image_profit = image_funds[fund_code]['profit']
        image_amount = image_funds[fund_code]['amount']
        total_image_profit += image_profit
        
        profit_diff = profit - image_profit
        
        status = "✅ 匹配" if abs(profit_diff) < 1 else "⚠️ 差异"
        
        print(f"{fund_code:<10} {fund_name[:30]:<30} {market_value:<12.2f} {image_amount:<12.2f} {profit_diff:<12.2f} {status:<10}")
    else:
        print(f"{fund_code:<10} {fund_name[:30]:<30} {market_value:<12.2f} {'N/A':<12} {'N/A':<12} ❌ 未匹配")

print("-" * 100)
print(f"\n{'总计':<40} {total_db_market_value:<12.2f}")

print(f"\n=== 汇总对比 ===")
print(f"数据库总成本: {total_db_cost:.2f}")
print(f"数据库总市值: {total_db_market_value:.2f}")
print(f"数据库总盈亏: {total_db_profit:.2f}")
print(f"图片总盈亏: {total_image_profit:.2f}")
print(f"盈亏差异: {total_db_profit - total_image_profit:.2f}")

# 检查图片中有但数据库中没有的基金
print(f"\n=== 图片中有但数据库中没有的基金 ===")
for code, data in image_funds.items():
    if code not in [f['fund_code'] for f in db_funds]:
        print(f"{code}: {data['name']} - 盈亏: {data['profit']:.2f}")

conn.close()
