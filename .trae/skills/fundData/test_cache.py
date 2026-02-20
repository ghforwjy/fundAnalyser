from smart_fund_data import get_value_averaging_report_text

print('第一次调用（应该重新计算）:')
report = get_value_averaging_report_text('018956', 100000, simulate=False)
print(report)

print()
print('='*70)
print('第二次调用（应该使用缓存）:')
report = get_value_averaging_report_text('018956', 100000, simulate=False)
print(report)
