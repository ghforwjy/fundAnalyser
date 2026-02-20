from portfolio_manager import get_portfolio_profit_loss_report

# 计算从2025-12-31到今天的盈亏
result = get_portfolio_profit_loss_report(
    portfolio_id=2,
    from_date='2025-12-31',
    to_date='2026-02-16'
)

if result.get('success'):
    print("=" * 80)
    print("组合盈亏报告")
    print("=" * 80)
    print(f"组合: {result.get('portfolio_name')} (ID: {result.get('portfolio_id')})")
    print(f"报告期间: {result.get('from_date')} 至 {result.get('to_date')}")
    print(f"基金数量: {result.get('fund_count')}")
    print()
    print(f"期初总市值: {result.get('start_market_value', 0):,.2f} 元")
    print(f"期末总市值: {result.get('end_market_value', 0):,.2f} 元")
    print(f"总盈亏: {result.get('total_profit_loss', 0):,.2f} 元")
    print(f"收益率: {result.get('total_return_rate', 0):.2f}%")
    print()
    
    details = result.get('details', [])
    if details:
        print("各基金盈亏明细:")
        print("-" * 80)
        print(f"{'基金代码':<10} {'基金名称':<25} {'期初市值':>12} {'期末市值':>12} {'盈亏':>12} {'收益率':>8}")
        print("-" * 80)
        for d in details:
            code = d.get('fund_code', '')
            name = d.get('fund_name', '')[:20]
            start_mv = d.get('start_market_value', 0)
            end_mv = d.get('end_market_value', 0)
            profit = d.get('profit_loss', 0)
            ret = d.get('return_rate', 0)
            print(f"{code:<10} {name:<25} {start_mv:>12.2f} {end_mv:>12.2f} {profit:>12.2f} {ret:>7.2f}%")
else:
    print(f"计算失败: {result.get('error')}")
