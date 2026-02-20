"""
模拟前端调用添加基金流程
"""
import requests
import json

base_url = "http://127.0.0.1:8000"
group_id = 3
fund_code = "021094"
shares = 150000
profit_loss = 1500

print("=== 模拟前端添加基金流程 ===")

# 第一步：添加基金到组合
print(f"\n1. 添加基金 {fund_code} 到组合 {group_id}")
add_response = requests.post(
    f"{base_url}/api/portfolio/groups/{group_id}/funds",
    json={
        "fund_code": fund_code,
        "shares": shares
    }
)
print(f"   响应: {add_response.status_code}")
print(f"   数据: {add_response.json()}")

# 第二步：录入盈亏数据
print(f"\n2. 录入盈亏数据")
profit_response = requests.post(
    f"{base_url}/api/portfolio/groups/{group_id}/profit-import",
    json={
        "profit_data": [{
            "fund_code": fund_code,
            "profit_loss": profit_loss
        }],
        "import_mode": "overwrite"
    }
)
print(f"   响应: {profit_response.status_code}")
print(f"   数据: {profit_response.json()}")

# 第三步：检查基金数据
print(f"\n3. 检查基金数据")
funds_response = requests.get(
    f"{base_url}/api/portfolio/groups/{group_id}/funds?force_refresh=false"
)
if funds_response.status_code == 200:
    data = funds_response.json()
    if data.get('success') and data.get('data'):
        for fund in data['data']:
            if fund['fund_code'] == fund_code:
                print(f"   基金: {fund['fund_name']}")
                print(f"   买入净值: {fund.get('buy_nav')}")
                print(f"   最新净值: {fund.get('latest_nav')}")
                print(f"   盈亏: {fund.get('profit_loss')}")
                print(f"   收益率: {fund.get('profit_rate')}%")
                break
