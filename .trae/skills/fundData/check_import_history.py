import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

portfolio_id = 2

print("=== 检查导入历史记录 ===")

c.execute("""
    SELECT 
        fund_code,
        fund_name,
        import_date,
        import_source
    FROM portfolio_fund
    WHERE portfolio_id = ? AND import_source IS NOT NULL
    ORDER BY fund_code
""", (portfolio_id,))

rows = c.fetchall()

print(f"\n共 {len(rows)} 只基金有导入记录\n")

for row in rows:
    print(f"{row['fund_code']}: {row['fund_name'][:30]} - {row['import_date']} - {row['import_source']}")

conn.close()
