"""
检查021094基金的数据
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData', 'fund_data.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

fund_code = '021094'

print(f"=== 检查基金 {fund_code} 的数据 ===")

# 检查 portfolio_fund
cursor.execute("""
    SELECT pf.*, p.name as portfolio_name
    FROM portfolio_fund pf
    JOIN portfolio p ON pf.portfolio_id = p.id
    WHERE pf.fund_code = ?
""", (fund_code,))

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"组合: {row['portfolio_name']}")
        print(f"基金代码: {row['fund_code']}")
        print(f"基金名称: {row['fund_name']}")
        print(f"份额: {row['shares']}")
        print(f"买入净值(buy_nav): {row['buy_nav']}")
        print(f"成本净值(cost_nav): {row['cost_nav']}")
        print(f"导入日期: {row['import_date']}")
        print(f"导入来源: {row['import_source']}")
        print()
else:
    print("portfolio_fund 表中没有数据")

# 检查 fund_nav
cursor.execute("""
    SELECT nav_date, unit_nav
    FROM fund_nav
    WHERE fund_code = ?
    ORDER BY nav_date DESC LIMIT 1
""", (fund_code,))

row = cursor.fetchone()
if row:
    print(f"最新净值: {row['unit_nav']} ({row['nav_date']})")
else:
    print("fund_nav 表中没有数据")

# 检查 fund_info
cursor.execute("""
    SELECT fund_name, fund_type
    FROM fund_info
    WHERE fund_code = ?
""", (fund_code,))

row = cursor.fetchone()
if row:
    print(f"基金信息: {row['fund_name']} ({row['fund_type']})")
else:
    print("fund_info 表中没有数据")

conn.close()
