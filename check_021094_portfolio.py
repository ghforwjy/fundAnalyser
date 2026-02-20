"""
检查021094在portfolio_fund中的数据
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData', 'fund_data.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

fund_code = '021094'

print(f"=== 检查portfolio_fund表中 {fund_code} 的数据 ===")

cursor.execute("""
    SELECT pf.*, p.name as portfolio_name
    FROM portfolio_fund pf
    JOIN portfolio p ON pf.portfolio_id = p.id
    WHERE pf.fund_code = ?
""", (fund_code,))

rows = cursor.fetchall()
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

conn.close()
