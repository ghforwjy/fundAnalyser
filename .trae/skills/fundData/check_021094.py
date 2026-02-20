"""
检查东方低碳经济混合A (021094) 的数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection
from portfolio_manager import calculate_fund_available_cash

def check_fund_data(portfolio_id=3, fund_code='021094'):
    """检查基金数据"""
    print(f"=" * 70)
    print(f"检查组合 {portfolio_id} 基金 {fund_code} (东方低碳经济混合A)")
    print(f"=" * 70)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. 查询所有买入交易
        print(f"\n【买入交易】")
        cursor.execute('''
            SELECT id, transaction_date, shares, amount, nav, notes
            FROM portfolio_transaction
            WHERE portfolio_id = ? AND fund_code = ? AND transaction_type = 'BUY'
            ORDER BY transaction_date
        ''', (portfolio_id, fund_code))

        buy_rows = cursor.fetchall()
        total_buy = 0
        for row in buy_rows:
            print(f"  ID:{row['id']} {row['transaction_date']} 份额:{row['shares']} 金额:{row['amount']} {row['notes'] or ''}")
            total_buy += row['amount']
        print(f"  买入合计: {total_buy}")

        # 2. 查询所有卖出交易
        print(f"\n【卖出交易】")
        cursor.execute('''
            SELECT id, transaction_date, shares, amount, nav, confirmed_nav, is_recovered, notes
            FROM portfolio_transaction
            WHERE portfolio_id = ? AND fund_code = ? AND transaction_type = 'SELL'
            ORDER BY transaction_date
        ''', (portfolio_id, fund_code))

        sell_rows = cursor.fetchall()
        total_sell = 0
        for row in sell_rows:
            print(f"  ID:{row['id']} {row['transaction_date']} 份额:{row['shares']} 金额:{row['amount']} nav:{row['nav']} confirmed_nav:{row['confirmed_nav']} is_recovered:{row['is_recovered']} {row['notes'] or ''}")
            total_sell += row['amount']
        print(f"  卖出合计: {total_sell}")

        # 3. 计算可用现金
        available_cash = total_sell - total_buy
        print(f"\n【现金计算】")
        print(f"  卖出合计: {total_sell}")
        print(f"  买入合计: {total_buy}")
        print(f"  可用现金: {available_cash}")

        # 4. 查询当前净值
        print(f"\n【当前净值】")
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
            print(f"  当前净值: {current_nav} ({nav_date})")

            # 5. 计算跌幅（针对未回收的卖出）
            print(f"\n【跌幅计算】")
            for row in sell_rows:
                if row['is_recovered'] == 0:
                    sell_nav = row['confirmed_nav'] or row['nav'] or (row['amount'] / row['shares'] if row['shares'] else 0)
                    if sell_nav and sell_nav > 0:
                        decline = (sell_nav - current_nav) / sell_nav
                        print(f"  卖出记录ID:{row['id']}")
                        print(f"    卖出净值: {sell_nav:.4f}")
                        print(f"    当前净值: {current_nav}")
                        print(f"    跌幅: {decline*100:.2f}%")
                        print(f"    是否达到20%阈值: {'✓ 是' if decline >= 0.20 else '✗ 否'}")
        else:
            print(f"  无净值数据")

        # 6. 函数计算结果
        print(f"\n【函数计算结果】")
        result = calculate_fund_available_cash(portfolio_id, fund_code)
        print(f"  {result}")

    print(f"\n" + "=" * 70)

if __name__ == '__main__':
    check_fund_data(3, '021094')
