import sqlite3

# 连接数据库
conn = sqlite3.connect('fund_data.db')
c = conn.cursor()

print("=== 检查 portfolio_fund 表字段顺序 ===")

c.execute("PRAGMA table_info(portfolio_fund)")
columns = c.fetchall()

for i, col in enumerate(columns):
    print(f"{i+1}. {col[1]} ({col[2]})")

conn.close()
