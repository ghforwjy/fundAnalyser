import akshare as ak

print('测试fund_portfolio_hold_em接口参数:')
print()

# 测试不带参数
print('1. 不带参数:')
try:
    df = ak.fund_portfolio_hold_em(symbol='018956')
    quarters = df['季度'].unique().tolist()
    print(f'   成功，获取到 {len(df)} 条记录')
    print(f'   季度: {quarters}')
except Exception as e:
    print(f'   失败: {e}')

print()

# 测试带年份参数
print('2. 带date="2024"参数:')
try:
    df = ak.fund_portfolio_hold_em(symbol='018956', date='2024')
    quarters = df['季度'].unique().tolist()
    print(f'   成功，获取到 {len(df)} 条记录')
    print(f'   季度: {quarters}')
except Exception as e:
    print(f'   失败: {e}')

print()

# 测试带年份参数2025
print('3. 带date="2025"参数:')
try:
    df = ak.fund_portfolio_hold_em(symbol='018956', date='2025')
    quarters = df['季度'].unique().tolist()
    print(f'   成功，获取到 {len(df)} 条记录')
    print(f'   季度: {quarters}')
except Exception as e:
    print(f'   失败: {e}')
