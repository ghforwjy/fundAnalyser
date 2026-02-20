import requests
import json

response = requests.get('http://localhost:8000/api/portfolio/groups/2/funds')
data = response.json()

if data.get('success'):
    funds = data['data']
    print(f"共 {len(funds)} 只基金\n")
    print(f"{'基金代码':<10} {'盈亏':<15} {'市值':<15}")
    print("-" * 50)
    for fund in funds:
        fund_code = fund['fund_code']
        profit_loss = fund.get('profit_loss')
        market_value = fund.get('market_value')
        print(f"{fund_code:<10} {str(profit_loss):<15} {str(market_value):<15}")
else:
    print("API调用失败:", data.get('message'))
