import sqlite3

conn = sqlite3.connect('fund.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("检查数据库中的基金数据")
print("=" * 80)

# 检查 018956
print("\n1. 检查 018956:")
cursor.execute("SELECT fund_code, fund_name, company_name, fund_type FROM fund_info WHERE fund_code = '018956'")
row = cursor.fetchone()
if row:
    print(f"   找到: {row['