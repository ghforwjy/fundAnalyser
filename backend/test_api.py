import sys
import asyncio
sys.path.insert(0, '.')
from api.portfolio import get_group_funds

async def test():
    result = await get_group_funds(1)
    if result['success']:
        print("API 返回数据:")
        for fund in result['data']:
            print(f"  {fund['fund_code']}: available_cash={fund.get('available_cash')}")
    else:
        print(f"Error: {result.get('message')}")

asyncio.run(test())
