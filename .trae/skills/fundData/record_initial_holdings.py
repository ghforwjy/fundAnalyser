from portfolio_manager import list_portfolio_funds, record_holding
from datetime import datetime

funds = list_portfolio_funds(2)
record_date = '2025-12-31'  # 图片中的数据日期

print(f"记录持仓快照，日期: {record_date}\n")
print("-" * 60)

success_count = 0
for f in funds:
    fund_code = f['fund_code']
    shares = f.get('shares') or 0
    
    if shares > 0:
        result = record_holding(
            portfolio_id=2,
            fund_code=fund_code,
            shares=shares,
            record_date=record_date,
            notes='初始持仓导入'
        )
        if result['success']:
            success_count += 1
            print(f"✓ {fund_code}: 份额 {shares:.2f}, 市值 {result.get('market_value', 0):.2f}")
        else:
            print(f"✗ {fund_code}: {result.get('error')}")

print("-" * 60)
print(f"\n成功记录 {success_count}/{len(funds)} 只基金持仓")
