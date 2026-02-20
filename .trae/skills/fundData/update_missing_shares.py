from portfolio_manager import update_portfolio_fund

# 补充缺失的基金份额
holdings = {
    '000930': 36.97,
    '001052': 18463.66,
    '021489': 2525.91,
    '021492': 8614.15,
    '022853': 7675.5,
    '024291': 10,
    '024389': 10020.04,
}

portfolio_id = 2
success_count = 0

for fund_code, shares in holdings.items():
    result = update_portfolio_fund(portfolio_id, fund_code, shares=shares)
    if result['success']:
        success_count += 1
        print(f"✓ {fund_code}: 更新份额 {shares}")
    else:
        print(f"✗ {fund_code}: {result.get('error')}")

print(f"\n成功更新 {success_count}/{len(holdings)} 只基金")
