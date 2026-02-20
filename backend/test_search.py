import requests
import json

print("=" * 80)
print("测试前端调用的 API")
print("=" * 80)

# 测试1: 搜索 018956
print("\n1. 搜索 018956:")
resp = requests.get("http://localhost:8000/api/funds", params={"keyword": "018956"})
data = resp.json()
print(f"   success: {data.get('success')}")
print(f"   total: {data.get('data', {}).get('total', 0)}")
if data.get('data', {}).get('data'):
    fund = data['data']['data'][0]
    print(f"   找到: {fund['fund_code']} - {fund['fund_name']}")

# 测试2: 搜索 000001
print("\n2. 搜索 000001:")
resp = requests.get("http://localhost:8000/api/funds", params={"keyword": "000001"})
data = resp.json()
print(f"   success: {data.get('success')}")
print(f"   total: {data.get('data', {}).get('total', 0)}")
if data.get('data', {}).get('data'):
    for fund in data['data']['data'][:3]:
        print(f"   找到: {fund['fund_code']} - {fund['fund_name']}")

# 测试3: 获取基金类型列表
print("\n3. 获取基金类型列表:")
resp = requests.get("http://localhost:8000/api/filters/fund-types")
data = resp.json()
print(f"   success: {data.get('success')}")
print(f"   types: {data.get('data', [])[:5]}...")

# 测试4: 获取基金公司列表
print("\n4. 获取基金公司列表:")
resp = requests.get("http://localhost:8000/api/filters/companies")
data = resp.json()
print(f"   success: {data.get('success')}")
print(f"   companies count: {len(data.get('data', []))}")
companies = data.get('data', [])
print(f"   前5个: {companies[:5]}")

# 测试5: 检查 018956 的公司名称
print("\n5. 检查 018956 的公司名称:")
resp = requests.get("http://localhost:8000/api/funds/018956")
data = resp.json()
if data.get('success'):
    fund = data.get('data', {})
    print(f"   fund_code: {fund.get('fund_code')}")
    print(f"   fund_name: {fund.get('fund_name')}")
    print(f"   company_name: '{fund.get('company_name')}'")
    print(f"   company_name is None: {fund.get('company_name') is None}")
    print(f"   company_name == '': {fund.get('company_name') == ''}")
