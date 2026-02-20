"""
检查AKShare版本和原始数据
"""
import akshare as ak
import requests
import json

print(f"AKShare版本: {ak.__version__}")

fund_code = '159566'
print(f"\n=== 尝试直接获取基金 {fund_code} 的分析数据 ===")

# 尝试直接调用蛋卷基金的API
url = f"https://danjuanapp.com/djapi/fund/{fund_code}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:2000]}")
except Exception as e:
    print(f"请求失败: {e}")
