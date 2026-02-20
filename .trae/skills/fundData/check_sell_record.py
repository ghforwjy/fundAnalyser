"""
检查卖出记录详情
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection

def check_sell_transactions(fund_code='016482'):
    """检查指定基金的卖出记录"""
    print(f"=" * 60)
    print(f"检查基金 {fund_code} 的卖出记录")
    print(f"=" * 60)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查询所有卖出记录
        cursor.execute('''
            SELECT id, portfolio_id, fund_code, transaction_type,
                   transaction_date, shares, amount, nav, confirmed_nav,
                   is_recovered, notes
            FROM portfolio_transaction
            WHERE fund_code = ? AND transaction_type = 'SELL'
            ORDER BY transaction_date DESC
        ''', (fund_code,))

        rows = cursor.fetchall()

        if not rows:
            print(f"\n基金 {fund_code} 没有卖出记录")
            return

        print(f"\n找到 {len(rows)} 条卖出记录:\n")

        for row in rows:
            print(f"记录ID: {row['id']}")
            print(f"  组合ID: {row['portfolio_id']}")
            print(f"  交易日期: {row['transaction_date']}")
            print(f"  卖出份额: {row['shares']}")
            print(f"  卖出金额: {row['amount']}")
            print(f"  nav字段: {row['nav']}")
            print(f"  confirmed_nav字段: {row['confirmed_nav']}")
            print(f"  is_recovered: {row['is_recovered']}")

            # 计算实际卖出净值
            if row['shares'] and row['shares'] > 0:
                calculated_nav = row['amount'] / row['shares']
                print(f"  计算净值(金额/份额): {calculated_nav:.4f}")

            # 使用哪个净值
            used_nav = row['confirmed_nav'] or row['nav'] or calculated_nav
            print(f"  算法将使用的净值: {used_nav}")
            print()

        # 查询当前净值
        print("-" * 60)
        cursor.execute('''
            SELECT unit_nav, nav_date
            FROM fund_nav
            WHERE fund_code = ?
            ORDER BY nav_date DESC
            LIMIT 1
        ''', (fund_code,))

        nav_row = cursor.fetchone()
        if nav_row:
            current_nav = nav_row['unit_nav']
            nav_date = nav_row['nav_date']
            print(f"\n当前净值 ({nav_date}): {current_nav}")

            # 计算跌幅
            for row in rows:
                if row['is_recovered'] == 0:  # 只计算未回收的
                    sell_nav = row['confirmed_nav'] or row['nav'] or (row['amount'] / row['shares'] if row['shares'] else 0)
                    if sell_nav and sell_nav > 0:
                        decline = (sell_nav - current_nav) / sell_nav
                        print(f"\n  相对于记录ID {row['id']}:")
                        print(f"    卖出净值: {sell_nav:.4f}")
                        print(f"    当前净值: {current_nav}")
                        print(f"    跌幅: {decline*100:.2f}%")
                        print(f"    是否达到20%阈值: {'是' if decline >= 0.20 else '否'}")

    print(f"\n" + "=" * 60)


if __name__ == '__main__':
    # 检查永赢高端装备智选混合发起C (016482)
    check_sell_transactions('016482')

    # 也检查所有有卖出记录的基金
    print("\n\n" + "=" * 60)
    print("所有有卖出记录的基金:")
    print("=" * 60)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT fund_code
            FROM portfolio_transaction
            WHERE transaction_type = 'SELL'
        ''')
        funds = cursor.fetchall()
        for fund in funds:
            print(f"  - {fund['fund_code']}")
