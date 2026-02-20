"""
查询基金名称
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import SmartFundData

# 基金代码列表
fund_codes = ['000143', '004011', '006331', '009424', '013431', '018957', '024291', '160514', '501022']

smart = SmartFundData()

print("基金代码与名称对照表：")
print("=" * 50)

for code in fund_codes:
    fund_info = smart._get_fund_info(code)
    if fund_info:
        print(f"{code}: {fund_info['fund_name']}")
    else:
        print(f"{code}: 未找到")
