import sqlite3

# 连接数据库
conn = sqlite3.connect('fund.db')
c = conn.cursor()

print("=== 检查数据库中的所有表 ===")

# 获取所有表名
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("\n数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
except Exception as e:
    print(f"获取表列表失败: {e}")

print("\n=== 检查fund_info表结构 ===")

# 检查fund_info表结构
try:
    c.execute("PRAGMA table_info(fund_info)")
    columns = c.fetchall()
    print("\nfund_info表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except Exception as e:
    print(f"获取fund_info表结构失败: {e}")

print("\n=== 检查fund_nav表结构 ===")

# 检查fund_nav表结构
try:
    c.execute("PRAGMA table_info(fund_nav)")
    columns = c.fetchall()
    print("\nfund_nav表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except Exception as e:
    print(f"获取fund_nav表结构失败: {e}")

print("\n=== 检查是否存在portfolio相关表 ===")

# 查找可能的portfolio相关表
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%portfolio%';")
    portfolio_tables = c.fetchall()
    print("\nPortfolio相关表:")
    for table in portfolio_tables:
        print(f"  - {table[0]}")
except Exception as e:
    print(f"查找portfolio表失败: {e}")

print("\n=== 检查是否存在holding相关表 ===")

# 查找可能的holding相关表
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%holding%';")
    holding_tables = c.fetchall()
    print("\nHolding相关表:")
    for table in holding_tables:
        print(f"  - {table[0]}")
except Exception as e:
    print(f"查找holding表失败: {e}")

# 关闭连接
conn.close()
