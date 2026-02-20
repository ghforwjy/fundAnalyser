"""
测试自计算风险指标
"""
import sys
import os

skill_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills', 'fundData')
sys.path.insert(0, skill_path)

from risk_metrics_calculator import calculate_fund_risk_metrics

fund_code = '159566'
print(f"=== 自计算基金 {fund_code} 的风险指标 ===")

result = calculate_fund_risk_metrics(fund_code, '近1年', force_update=True)
print(f"结果: {result}")
