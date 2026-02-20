import sys
sys.path.insert(0, r'd:\mycode\fundAnalyser\.trae\skills\fundData')
from portfolio_manager import add_funds_to_portfolio

fund_codes = [
    '000330', '001052', '003003', '022853', '021492', '024389', '021489',
    '000397', '000930', '000607', '024291', '000343',
    '000143', '007994', '501022', '160514', '009424', '000217',
    '001595', '013431', '004011', '486001', '010108', '006331', '018957'
]

result = add_funds_to_portfolio(2, fund_codes, exclude_money_market=True)
print(f'成功: {result["success_count"]}')
print(f'排除(货币基金): {result["excluded_count"]}')
print(f'失败: {result["failed_count"]}')
print('\n详情:')
for detail in result['details']:
    if detail['status'] == 'excluded':
        print(f'  - {detail["fund_code"]}: 已排除(货币基金)')
    elif detail['status'] == 'failed':
        print(f'  - {detail["fund_code"]}: 失败 - {detail.get("error", "")}')
