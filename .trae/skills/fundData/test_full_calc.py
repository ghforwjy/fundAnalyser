"""
测试完整的止盈建议计算
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit import TakeProfitCalculator
from take_profit_manager import TakeProfitTemplateManager
from portfolio_manager import calculate_portfolio_available_cash_batch

def test_full_calculation(portfolio_id=3):
    """测试完整计算"""
    print("=" * 70)
    print(f"测试组合 {portfolio_id} 的完整止盈建议计算")
    print("=" * 70)

    calculator = TakeProfitCalculator()
    result = calculator.calculate_portfolio(portfolio_id)

    print(f"\n【汇总】")
    print(f"  总基金数: {result['summary']['total_funds']}")
    print(f"  建议卖出: {result['summary']['need_action_count']}")
    print(f"  建议捡回: {result['summary']['buy_back_count']}")
    print(f"  继续持有: {result['summary']['hold_count']}")

    print(f"\n【各基金详情】")
    for fund in result['funds']:
        print(f"\n  {fund['fund_code']} - {fund['fund_name']}")
        print(f"    动作: {fund['action']}")
        print(f"    原因: {fund['reason']}")
        print(f"    未回收卖出: {fund['unrecovered_sells_count']}")
        if fund['action'] == 'BUY':
            print(f"    捡回份额: {fund['buy_back_shares']}")
            print(f"    捡回金额: {fund['buy_back_amount']}")
        # 打印算法详情中的关键信息
        for detail in fund['algorithm_details']:
            if '波段捡回' in detail or 'enable_buy_back' in detail:
                print(f"    > {detail}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_full_calculation(3)
