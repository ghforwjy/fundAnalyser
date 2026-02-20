"""
检查所有卖出记录详情
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection

def check_all_sell_transactions():
    """检查所有卖出记录"""
    print(f"=" * 70)
    print(f"检查所有卖出记录")
    print(f"=" * 70)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查询所有卖出记录
        cursor.execute('''
            SELECT pt.id, pt.portfolio_id, pt.fund_code, fi.fund_name,
                   pt.transaction_date, pt.shares, pt.amount, pt.nav, pt.confirmed_nav,
                   pt.is_recovered, pt.notes
            FROM portfolio_transaction pt
            LEFT JOIN fund_info fi ON pt.fund_code = fi.fund_code
            WHERE pt.transaction_type = 'SELL'
            ORDER BY pt.transaction_date DESC
        ''')

        rows = cursor.fetchall()

        if not rows:
            print(f"\n没有卖出记录")
            return

        print(f"\n找到 {len(rows)} 条卖出记录:\n")

        for row in rows:
            fund_name = row['fund_name'] or '未知基金'
            print(f"记录ID: {row['id']} | 组合ID: {row['portfolio_id']}")
            print(f"  基金: {row['fund_code']} - {fund_name}")
            print(f"  日期: {row['transaction_date']}")
            print(f"  份额: {row['shares']} | 金额: ¥{row['amount']}")
            print(f"  nav: {row['nav']} | confirmed_nav: {row['confirmed_nav']}")

            # 计算实际卖出净值
            if row['shares'] and row['shares'] > 0:
                calculated_nav = row['amount'] / row['shares']
                print(f"  计算净值: {calculated_nav:.4f}")

            print(f"  is_recovered: {row['is_recovered']}")
            print()

        # 检查每个基金的当前净值和跌幅
        print("-" * 70)
        print("\n当前净值和跌幅分析:\n")

        fund_codes = set(row['fund_code'] for row in rows if row['is_recovered'] == 0)

        for fund_code in fund_codes:
            # 获取最新净值
            cursor.execute('''
                SELECT unit_nav, nav_date
                FROM fund_nav
                WHERE fund_code = ?
                ORDER BY nav_date DESC
                LIMIT 1
            ''', (fund_code,))

            nav_row = cursor.fetchone()
            if not nav_row:
                print(f"{fund_code}: 无净值数据")
                continue

            current_nav = nav_row['unit_nav']
            nav_date = nav_row['nav_date']

            # 获取该基金的未回收卖出记录
            cursor.execute('''
                SELECT id, shares, amount, confirmed_nav, nav
                FROM portfolio_transaction
                WHERE fund_code = ? AND transaction_type = 'SELL' AND is_recovered = 0
                ORDER BY transaction_date DESC
                LIMIT 1
            ''', (fund_code,))

            sell_row = cursor.fetchone()
            if not sell_row:
                continue

            sell_nav = sell_row['confirmed_nav'] or sell_row['nav'] or (sell_row['amount'] / sell_row['shares'] if sell_row['shares'] else 0)

            if sell_nav and sell_nav > 0:
                decline = (sell_nav - current_nav) / sell_nav
                print(f"{fund_code}:")
                print(f"  卖出净值: {sell_nav:.4f}")
                print(f"  当前净值: {current_nav} ({nav_date})")
                print(f"  跌幅: {decline*100:.2f}%")
                print(f"  达到20%阈值: {'✓ 是' if decline >= 0.20 else '✗ 否'}")
                print()

    print(f"=" * 70)


if __name__ == '__main__':
    check_all_sell_transactions()
