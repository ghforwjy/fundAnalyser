from portfolio_manager import PortfolioManager

pm = PortfolioManager()
result = pm.get_portfolio_profit_loss_report(2, '2025-12-31', '2026-02-16')

print("=" * 100)
print("组合盈亏报告")
print("=" * 100)
print(f"组合: {result.get('portfolio_name')} (ID: {result.get('portfolio_id')})")
print(f"报告期间: {result.get('from_date')} 至 {result.get('to_date')}")
print()

start_value = result.get('total_value_from', 0)
end_value = result.get('total_value_to', 0)
profit = result.get('total_profit_loss', 0)
return_rate = (profit / start_value * 100) if start_value > 0 else 0

print(f"期初总市值: {start_value:,.2f} 元")
print(f"期末总市值: {end_value:,.2f} 元")
print(f"总盈亏: {profit:,.2f} 元")
print(f"收益率: {return_rate:.2f}%")
print()

funds = result.get('funds', [])
if funds:
    print("各基金盈亏明细:")
    print("-" * 100)
    print(f"{'基金代码':<10} {'基金名称':<28} {'期初市值':>14} {'期末市值':>14} {'盈亏':>14} {'收益率':>10}")
    print("-" * 100)
    
    # 按盈亏排序
    funds_sorted = sorted(funds, key=lambda x: x.get('profit_loss', 0), reverse=True)
    
    for f in funds_sorted:
        code = f.get('fund_code', '')
        name = f.get('fund_name', '')[:25]
        start_mv = f.get('value_from', 0)
        end_mv = f.get('value_to', 0)
        profit_loss = f.get('profit_loss', 0)
        ret = (profit_loss / start_mv * 100) if start_mv > 0 else 0
        print(f"{code:<10} {name:<28} {start_mv:>14,.2f} {end_mv:>14,.2f} {profit_loss:>+14,.2f} {ret:>9.2f}%")

print("-" * 100)
