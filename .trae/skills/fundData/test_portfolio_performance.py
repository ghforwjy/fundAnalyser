import sys
sys.path.append('d:\\mycode\\fundAnalyser\\.trae\\skills\\fundData')
from smart_fund_data import get_portfolio_funds_full
import time

print('测试组合查询性能...')
start = time.time()
result = get_portfolio_funds_full(portfolio_id=2)
end = time.time()

print(f'查询耗时: {end - start:.2f} 秒')
print(f'基金数量: {len(result.get("funds", []))}')
print(f'新鲜度统计: {result.get("freshness_summary", {})}')

# 分析每只基金的处理时间
print('\n分析每只基金的处理时间:')
funds = result.get('funds', [])
for i, fund in enumerate(funds[:5], 1):
    print(f'{i}. {fund["fund_code"]} - {fund["fund_name"]}')
    print(f'   净值日期: {fund.get("nav_date", "-")}')
    print(f'   风险指标更新时间: {fund.get("metrics_update_time", "-")}')
