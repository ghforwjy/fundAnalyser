"""
检查风险指标同步
"""
import sys
import os

# 添加 skill 路径
skill_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData')
sys.path.insert(0, skill_path)

from syncers.group_syncers import sync_single_fund_risk

fund_code = '159566'
print(f"=== 同步基金 {fund_code} 的风险指标 ===")

result = sync_single_fund_risk(fund_code)
print(f"结果: {result}")
