"""
搜索领航系列基金
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData

smart = SmartFundData()

# 用关键词搜索领航
print('搜索包含"领航"的基金：')
print('=' * 100)
linghang_funds = smart.query_funds(keyword='领航', limit=100)

print(f"{'基金代码':<10} {'基金名称':<50} {'基金类型':<20}")
print('-' * 100)

for f in linghang_funds:
    name = f['fund_name'][:47] + '..' if len(f['fund_name']) > 49 else f['fund_name']
    fund_type = f['fund_type'][:17] if len(f['fund_type']) > 19 else f['fund_type']
    print(f"{f['fund_code']:<10} {name:<50} {fund_type:<20}")

print('=' * 100)
print(f'总计：{len(linghang_funds)} 只')

# 筛选中航基金的领航系列
print('\n\n中航基金旗下的领航系列：')
print('-' * 100)
zh_linghang = [f for f in linghang_funds if '中航' in f['fund_name'] or '中航' in f.get('company_name', '')]
for f in zh_linghang:
    print(f"{f['fund_code']:<10} {f['fund_name']:<50} {f['fund_type']:<20}")
print(f'中航领航系列总计：{len(zh_linghang)} 只')
