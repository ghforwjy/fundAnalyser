from smart_fund_data import get_fund_holdings, format_holdings_report

print('测试持仓查询:')
holdings = get_fund_holdings('中航机遇领航')
print(format_holdings_report(holdings))
