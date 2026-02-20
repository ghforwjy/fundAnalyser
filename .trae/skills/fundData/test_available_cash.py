"""
测试成分基金可用现金计算功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import (
    calculate_fund_available_cash,
    get_portfolio_funds_available_cash,
    list_portfolios,
    list_portfolio_funds
)
from smart_fund_data import get_portfolio_funds_full, format_portfolio_report


def test_calculate_fund_available_cash():
    """测试单只基金可用现金计算"""
    print("=" * 80)
    print("测试1: 单只基金可用现金计算")
    print("=" * 80)

    portfolios = list_portfolios()
    if not portfolios:
        print("没有找到任何组合，请先创建组合")
        return

    portfolio_id = portfolios[0]['id']
    print(f"使用组合ID: {portfolio_id}")

    funds = list_portfolio_funds(portfolio_id)
    if not funds:
        print("组合中没有基金")
        return

    # 测试第一只基金
    fund_code = funds[0]['fund_code']
    print(f"测试基金: {fund_code}")

    result = calculate_fund_available_cash(portfolio_id, fund_code)
    print(f"结果: {result}")


def test_get_portfolio_funds_available_cash():
    """测试批量获取所有基金可用现金"""
    print("\n" + "=" * 80)
    print("测试2: 批量获取所有基金可用现金")
    print("=" * 80)

    portfolios = list_portfolios()
    if not portfolios:
        print("没有找到任何组合")
        return

    portfolio_id = portfolios[0]['id']
    result = get_portfolio_funds_available_cash(portfolio_id)

    if result['success']:
        print(f"组合: {result['portfolio_name']}")
        print(f"基金数量: {result['fund_count']}")
        print(f"总可用现金: {result.get('total_available_cash', 0)}")
        print("\n各基金可用现金:")
        for fund in result['funds']:
            cash = fund['available_cash']
            status = "净卖出" if cash > 0 else ("净投入" if cash < 0 else "平衡")
            print(f"  {fund['fund_code']} - {fund['fund_name']}: {cash:,.2f} ({status})")
    else:
        print(f"错误: {result.get('error')}")


def test_get_portfolio_funds_full():
    """测试聚合查询中包含可用现金"""
    print("\n" + "=" * 80)
    print("测试3: 聚合查询中包含可用现金字段")
    print("=" * 80)

    portfolios = list_portfolios()
    if not portfolios:
        print("没有找到任何组合")
        return

    portfolio_id = portfolios[0]['id']
    result = get_portfolio_funds_full(portfolio_id)

    if 'error' in result:
        print(f"错误: {result['error']}")
        return

    print(f"组合: {result['portfolio_name']}")
    print(f"基金数量: {result['fund_count']}")

    # 检查每只基金是否有可用现金字段
    print("\n检查可用现金字段:")
    for fund in result['funds']:
        fund_code = fund['fund_code']
        if 'available_cash' in fund:
            cash = fund['available_cash']
            print(f"  {fund_code}: available_cash = {cash:,.2f}")
        else:
            print(f"  {fund_code}: 无 available_cash 字段")


def test_format_portfolio_report():
    """测试格式化报告中显示可用现金"""
    print("\n" + "=" * 80)
    print("测试4: 格式化报告中显示可用现金")
    print("=" * 80)

    portfolios = list_portfolios()
    if not portfolios:
        print("没有找到任何组合")
        return

    portfolio_id = portfolios[0]['id']
    result = get_portfolio_funds_full(portfolio_id)

    if 'error' in result:
        print(f"错误: {result['error']}")
        return

    report = format_portfolio_report(result)
    print(report)


if __name__ == '__main__':
    print("成分基金可用现金计算功能测试")
    print("=" * 80)

    try:
        test_calculate_fund_available_cash()
    except Exception as e:
        print(f"测试1失败: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_get_portfolio_funds_available_cash()
    except Exception as e:
        print(f"测试2失败: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_get_portfolio_funds_full()
    except Exception as e:
        print(f"测试3失败: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_format_portfolio_report()
    except Exception as e:
        print(f"测试4失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
