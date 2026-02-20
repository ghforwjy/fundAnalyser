"""
最终测试 - 定投计算性能和正确性
"""
import time
import requests

# 测试API
url = "http://127.0.0.1:8000/api/portfolio/groups/2/investment-advice?mode=value_averaging&simulate=true"

print("=" * 60)
print("测试定投计算（含新鲜度检查）")
print("=" * 60)

start_time = time.time()
response = requests.post(url)
elapsed = time.time() - start_time

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        funds = data['data']['funds']
        print(f"\n✓ 计算完成: {len(funds)} 只基金")
        print(f"✓ 总耗时: {elapsed:.2f} 秒")
        print(f"✓ 平均每只: {elapsed/len(funds):.2f} 秒")
        print()
        
        # 显示前3只基金的结果
        print("前3只基金计算结果:")
        print("-" * 60)
        for fund in funds[:3]:
            print(f"\n{fund['fund_name']} ({fund['fund_code']})")
            print(f"  基准市值: ¥{fund['base_value']:,.2f}")
            print(f"  当前市值: ¥{fund['actual_value']:,.2f}")
            print(f"  建议操作: {fund['invest_action']} ¥{abs(fund['suggested_invest']):,.2f}")
    else:
        print(f"✗ API返回错误: {data.get('message')}")
else:
    print(f"✗ 请求失败: {response.status_code}")

print("\n" + "=" * 60)
