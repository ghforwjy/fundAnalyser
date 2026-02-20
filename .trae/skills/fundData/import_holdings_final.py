from portfolio_manager import add_funds_to_portfolio

# 2025年12月31日持仓数据（排除货币基金）
holdings = {
    # 第一张图 - 非货币基金
    '001052': {'shares': 18463.66, 'buy_date': '2025-12-31', 'buy_nav': 0.8959, 'notes': '2025年底持仓'},
    '022853': {'shares': 7675.50, 'buy_date': '2025-12-31', 'buy_nav': 1.6224, 'notes': '2025年底持仓'},
    '021492': {'shares': 8614.15, 'buy_date': '2025-12-31', 'buy_nav': 1.2789, 'notes': '2025年底持仓'},
    '024389': {'shares': 10020.04, 'buy_date': '2025-12-31', 'buy_nav': 1.0477, 'notes': '2025年底持仓'},
    '021489': {'shares': 2525.91, 'buy_date': '2025-12-31', 'buy_nav': 2.7528, 'notes': '2025年底持仓'},
    '000930': {'shares': 36.97, 'buy_date': '2025-12-31', 'buy_nav': 9.2770, 'notes': '2025年底持仓'},
    '024291': {'shares': 10.00, 'buy_date': '2025-12-31', 'buy_nav': 1.0015, 'notes': '2025年底持仓'},
    
    # 第二张图 - 非货币基金
    '000143': {'shares': 182353.51, 'buy_date': '2025-12-31', 'buy_nav': 2.0710, 'notes': '2025年底持仓'},
    '007994': {'shares': 98717.71, 'buy_date': '2025-12-31', 'buy_nav': 2.4212, 'notes': '2025年底持仓'},
    '501022': {'shares': 76188.69, 'buy_date': '2025-12-31', 'buy_nav': 2.5420, 'notes': '2025年底持仓'},
    '160514': {'shares': 60562.02, 'buy_date': '2025-12-31', 'buy_nav': 1.8615, 'notes': '2025年底持仓'},
    '009424': {'shares': 90220.13, 'buy_date': '2025-12-31', 'buy_nav': 1.2225, 'notes': '2025年底持仓'},
    '000217': {'shares': 22582.35, 'buy_date': '2025-12-31', 'buy_nav': 3.3015, 'notes': '2025年底持仓'},
    '001595': {'shares': 38155.32, 'buy_date': '2025-12-31', 'buy_nav': 1.7562, 'notes': '2025年底持仓'},
    '013431': {'shares': 49409.19, 'buy_date': '2025-12-31', 'buy_nav': 1.2313, 'notes': '2025年底持仓'},
    '004011': {'shares': 33606.67, 'buy_date': '2025-12-31', 'buy_nav': 1.5407, 'notes': '2025年底持仓'},
    '486001': {'shares': 24946.76, 'buy_date': '2025-12-31', 'buy_nav': 1.5800, 'notes': '2025年底持仓'},
    '010108': {'shares': 20823.05, 'buy_date': '2025-12-31', 'buy_nav': 0.7983, 'notes': '2025年底持仓'},
    '006331': {'shares': 25376.42, 'buy_date': '2025-12-31', 'buy_nav': 1.2207, 'notes': '2025年底持仓'},
    '018957': {'shares': 7211.60, 'buy_date': '2025-12-31', 'buy_nav': 3.5560, 'notes': '2025年底持仓'},
}

print(f"准备导入 {len(holdings)} 只基金持仓数据...")
print("-" * 60)

# 导入到组合2
result = add_funds_to_portfolio(
    portfolio_id=2,
    holdings=holdings,
    exclude_money_market=True  # 排除货币基金
)

print(f"\n导入结果:")
print(f"  成功: {result['success_count']} 只")
print(f"  失败: {result['failed_count']} 只")
print(f"  排除(货币基金): {result['excluded_count']} 只")

if result['failed_count'] > 0:
    print("\n失败的基金:")
    for detail in result['details']:
        if detail['status'] == 'failed':
            print(f"  - {detail['fund_code']}: {detail.get('error')}")

if result['excluded_count'] > 0:
    print("\n排除的货币基金:")
    for detail in result['details']:
        if detail['status'] == 'excluded':
            print(f"  - {detail['fund_code']}: {detail.get('reason')}")
