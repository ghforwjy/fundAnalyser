"""
测试导入盈亏数据
"""
import sys
import os

skill_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData')
sys.path.insert(0, skill_path)

from portfolio_manager import PortfolioManager

pm = PortfolioManager()

# 测试导入盈亏数据
portfolio_id = 3  # 交易测试组合
fund_code = '021094'
profit_loss = 1500  # 盈利1500

print(f"=== 测试导入盈亏数据 ===")
print(f"组合ID: {portfolio_id}")
print(f"基金代码: {fund_code}")
print(f"盈亏: {profit_loss}")

result = pm.import_profit_data(
    portfolio_id=portfolio_id,
    profit_data=[{
        'fund_code': fund_code,
        'profit_loss': profit_loss
    }],
    import_mode='overwrite',
    source_type='manual'
)

print(f"\n结果: {result}")

# 检查数据库
import sqlite3
db_path = os.path.join(skill_path, 'fund_data.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT buy_nav, cost_nav, import_date, import_source
    FROM portfolio_fund
    WHERE portfolio_id = ? AND fund_code = ?
""", (portfolio_id, fund_code))

row = cursor.fetchone()
if row:
    print(f"\n更新后的数据:")
    print(f"  buy_nav: {row['buy_nav']}")
    print(f"  cost_nav: {row['cost_nav']}")
    print(f"  import_date: {row['import_date']}")
    print(f"  import_source: {row['import_source']}")
else:
    print("\n没有找到记录")

conn.close()
