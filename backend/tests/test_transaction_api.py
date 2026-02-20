"""
测试交易维护API接口
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'skills', 'fundData'))

from portfolio_manager import (
    create_portfolio,
    record_buy_transaction,
    record_sell_transaction,
    get_portfolio_transactions,
    get_portfolio_cash,
    update_portfolio_cash,
    add_funds_to_portfolio,
    list_portfolio_funds
)


def test_transaction_api():
    print("=" * 60)
    print("测试交易维护API")
    print("=" * 60)

    # 1. 创建测试组合
    print("\n1. 创建测试组合...")
    result = create_portfolio("交易测试组合", "用于测试交易功能")
    if not result['success']:
        print(f"创建组合失败: {result.get('error')}")
        return

    portfolio_id = result['portfolio_id']
    print(f"创建组合成功: ID={portfolio_id}")

    # 2. 添加初始基金
    print("\n2. 添加初始基金...")
    result = add_funds_to_portfolio(
        portfolio_id,
        {
            '000001': {
                'shares': 1000,
                'buy_date': '2026-01-01',
                'buy_nav': 1.5,
                'notes': '初始持仓'
            }
        }
    )
    print(f"添加基金结果: {result}")

    # 3. 测试买入交易
    print("\n3. 测试买入交易...")
    result = record_buy_transaction(
        portfolio_id=portfolio_id,
        fund_code='000001',
        shares=500,
        amount=800,
        transaction_date='2026-02-17',
        nav=1.6,
        notes='追加买入'
    )
    print(f"买入结果: {result}")

    if result['success']:
        print(f"  新持仓数量: {result['new_total_shares']}")
        print(f"  新成本净值: {result['new_buy_nav']}")

    # 4. 查看持仓
    print("\n4. 查看当前持仓...")
    funds = list_portfolio_funds(portfolio_id)
    for fund in funds:
        print(f"  {fund['fund_code']}: {fund['shares']}份, 成本净值: {fund['buy_nav']}")

    # 5. 测试卖出交易
    print("\n5. 测试卖出交易...")
    result = record_sell_transaction(
        portfolio_id=portfolio_id,
        fund_code='000001',
        shares=300,
        amount=500,
        transaction_date='2026-02-18',
        nav=1.7,
        notes='部分卖出'
    )
    print(f"卖出结果: {result}")

    if result['success']:
        print(f"  剩余持仓: {result['new_total_shares']}")
        print(f"  新成本净值: {result['new_buy_nav']}")
        print(f"  现金增加: {result['cash_added']}")
        print(f"  新现金余额: {result['new_cash_balance']}")

    # 6. 查看现金余额
    print("\n6. 查看现金余额...")
    result = get_portfolio_cash(portfolio_id)
    print(f"现金余额: {result}")

    # 7. 查看交易记录
    print("\n7. 查看交易记录...")
    transactions = get_portfolio_transactions(portfolio_id)
    for t in transactions:
        print(f"  {t['transaction_date']} {t['transaction_type']}: {t['shares']}份, 金额{t['amount']}")

    # 8. 测试全部卖出
    print("\n8. 测试全部卖出...")
    funds = list_portfolio_funds(portfolio_id)
    if funds:
        remaining_shares = funds[0]['shares']
        result = record_sell_transaction(
            portfolio_id=portfolio_id,
            fund_code='000001',
            shares=remaining_shares,
            amount=remaining_shares * 1.8,
            transaction_date='2026-02-19',
            nav=1.8,
            notes='全部卖出'
        )
        print(f"全部卖出结果: {result}")

    # 9. 查看最终状态
    print("\n9. 查看最终状态...")
    funds = list_portfolio_funds(portfolio_id)
    print(f"持仓数量: {len(funds)}")

    result = get_portfolio_cash(portfolio_id)
    if result['success']:
        print(f"最终现金余额: {result['cash']}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    test_transaction_api()
