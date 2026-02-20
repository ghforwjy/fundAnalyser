"""
查看中航基金所有基金列表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData

smart = SmartFundData()

# 查询所有中航基金
all_zh_funds = smart.query_funds(company='中航', limit=100)

print('中航基金所有基金列表：')
print('=' * 100)
print(f"{'基金代码':<10} {'基金名称':<50} {'基金类型':<20}")
print('-' * 100)

for f in all_zh_funds:
    name = f['fund_name'][:47] + '..' if len(f['fund_name']) > 49 else f['fund_name']
    fund_type = f['fund_type'][:17] if len(f['fund_type']) > 19 else f['fund_type']
    print(f"{f['fund_code']:<10} {name:<50} {fund_type:<20}")

print('=' * 100)
print(f'总计：{len(all_zh_funds)} 只')

# 筛选出领航系列
print('\n\n领航系列基金：')
print('-' * 100)
linghang_funds = [f for f in all_zh_funds if '领航' in f['fund_name']]
for f in linghang_funds:
    print(f"{f['fund_code']:<10} {f['fund_name']:<50} {f['fund_type']:<20}")
print(f'领航系列总计：{len(linghang_funds)} 只')
