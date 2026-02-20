"""
检查现金计算详情
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection
from portfolio_manager import calculate_fund_available_cash

def check_cash_calculation(portfolio_id=3, fund_code='015790'):
    """检查现金计算详情"""
    print(f"=" * 70)
    print(f"检查组合 {portfolio_id} 基金 {fund_code} 的现金计算")
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

        # 4. 对比函数计算结果
        print(f"\n【函数计算结果】")
        result = calculate_fund_available_cash(portfolio_id, fund_code)
        print(f"  {result}")

    print(f"\n" + "=" * 70)

if __name__ == '__main__':
    check_cash_calculation(3, '015790')
