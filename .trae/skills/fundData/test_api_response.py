"""
测试API返回的数据结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit import calculate_portfolio_take_profit
import json

def test_api_response(portfolio_id=3):
    """测试API返回的数据"""
    print("=" * 70)
    print(f"测试组合 {portfolio_id} 的API返回数据")
    print("=" * 70)

    result = calculate_portfolio_take_profit(portfolio_id)

    # 检查021094基金
    for fund in result['funds']:
        if fund['fund_code'] == '021094':
            print(f"\n【021094 基金数据】")
            print(f"  fund_code: {fund['fund_code']}")
            print(f"  fund_name: {fund['fund_name']}")
            print(f"  action: {fund['action']} (类型: {type(fund['action'])})")
            print(f"  action == 'BUY': {fund['action'] == 'BUY'}")
            print(f"  reason: {fund['reason']}")
            print(f"  buy_back_shares: {fund.get('buy_back_shares')}")
            print(f"  buy_back_amount: {fund.get('buy_back_amount')}")

    # 检查JSON序列化
    print(f"\n【JSON序列化测试】")
    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        for fund in parsed['funds']:
            if fund['fund_code'] == '021094':
                print(f"  JSON序列化后 action: {fund['action']} (类型: {type(fund['action'])})")
                print(f"  action == 'BUY': {fund['action'] == 'BUY'}")
    except Exception as e:
        print(f"  JSON序列化失败: {e}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_api_response(3)
