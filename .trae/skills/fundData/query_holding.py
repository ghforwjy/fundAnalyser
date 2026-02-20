from smart_fund_data import SmartFundData
from fund_data_skill import FundDataSkill

smart = SmartFundData()
skill = FundDataSkill()

print('='*60)
print('查找中航机遇领航基金')
print('='*60)

funds = smart.query_funds(keyword='中航机遇领航', limit=5)
print(f'\n找到 {len(funds)} 只基金:')
for f in funds:
    print(f'  代码: {f["fund_code"]}, 名称: {f["fund_name"]}, 类型: {f["fund_type"]}')

if funds:
    fund_code = funds[0]['fund_code']
    print(f'\n{"="*60}')
    print(f'查询 {fund_code} 的持仓数据')
    print(f'{"="*60}')
    
    result = skill.sync_group_holdings([fund_code])
    print(f'\n同步结果: {result["message"]}')
    
    holdings = skill.query_fund_holdings(fund_code, limit=20)
    if holdings:
        print(f'\n股票持仓 (前20):')
        print(f'{"股票代码":<10} {"股票名称":<12} {"持仓比例":>10} {"持仓市值":>15}')
        print('-'*50)
        for h in holdings:
            print(f'{h["stock_code"]:<10} {h["stock_name"]:<12} {h["hold_ratio"]:>10.2f}% {h["hold_value"]:>15,.0f}')
    else:
        print('未找到持仓数据')
