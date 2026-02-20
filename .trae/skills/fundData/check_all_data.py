from portfolio_manager import list_portfolio_funds
from database import get_db_connection
from datetime import datetime

funds = list_portfolio_funds(2)
print(f"组合中共有 {len(funds)} 只基金:\n")

print(f"{'基金代码':<10} {'基金名称':<30} {'份额':>12} {'更新日期':>20}")
print("-" * 80)

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    for f in funds:
        code = f['fund_code']
        name = f.get('fund_name', '未知')[:25]
        shares = f.get('shares') or 0
        
        # 查询净值更新历史
        cursor.execute('''
            SELECT MAX(nav_date) as latest_date, COUNT(*) as count
            FROM fund_nav
            WHERE fund_code = ?
        ''', (code,))
        row = cursor.fetchone()
        latest_date = row['latest_date'] if row else '无数据'
        nav_count = row['count'] if row else 0
        
        update_info = f"{latest_date} ({nav_count}条)"
        
        print(f"{code:<10} {name:<30} {shares:>12.2f} {update_info:>20}")

print("\n" + "=" * 80)
print("检查是否有份额为0的基金...")
print("=" * 80)

zero_shares = [f for f in funds if not f.get('shares')]
if zero_shares:
    print(f"\n发现 {len(zero_shares)} 只基金份额为0:")
    for f in zero_shares:
        print(f"  - {f['fund_code']} {f.get('fund_name', '')}")
else:
    print("\n所有基金都有份额数据！")
