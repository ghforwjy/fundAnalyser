from portfolio_manager import list_portfolio_funds

funds = list_portfolio_funds(2)
print(f"组合中共有 {len(funds)} 只基金:\n")

for f in funds:
    code = f['fund_code']
    name = f.get('fund_name', '未知')
    shares = f.get('shares') or 0
    print(f"{code} {name} - 份额: {shares}")
