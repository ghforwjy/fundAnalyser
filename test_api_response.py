"""
测试API返回的数据
"""
import requests

url = "http://127.0.0.1:8000/api/portfolio/groups/3/funds?force_refresh=false"
headers = {
    "Accept": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('data'):
            for fund in data['data']:
                if fund['fund_code'] == '159566':
                    print(f"基金: {fund['fund_name']}")
                    print(f"  买入净值: {fund.get('buy_nav')}")
                    print(f"  最新净值: {fund.get('latest_nav')}")
                    print(f"  盈亏: {fund.get('profit_loss')}")
                    print(f"  收益率: {fund.get('profit_rate')}%")
                    print(f"  近1年收益: {fund.get('return_1y')}%")
                    print(f"  最大回撤(1年): {fund.get('max_drawdown_1y')}%")
                    print(f"  夏普比率(1年): {fund.get('sharpe_ratio_1y')}")
                    print(f"  年化波动率(1年): {fund.get('annual_volatility_1y')}%")
                    print(f"  同类排名: {fund.get('rank_in_category')}")
                    break
        else:
            print(f"返回数据: {data}")
    else:
        print(f"请求失败: {response.text}")
except Exception as e:
    print(f"错误: {e}")
