import sys
sys.path.append('d:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')
from portfolio_manager import list_portfolios

portfolios = list_portfolios()
print('当前组合数量:', len(portfolios))
print('\n组合详情:')
for p in portfolios:
    print(f'ID: {p["id"]}, 名称: {p["name"]}, 基金数量: {p.get("fund_count", 0)}')

# 检查第一个组合的基金详情
if portfolios:
    portfolio_id = portfolios[0]['id']
    from portfolio_manager import list_portfolio_funds
    funds = list_portfolio_funds(portfolio_id)
    print(f'\n第一个组合(ID: {portfolio_id})的基金数量:', len(funds))
    print('前5只基金:')
    for i, fund in enumerate(funds[:5], 1):
        print(f'{i}. {fund["fund_code"]} - {fund["fund_name"]}')
