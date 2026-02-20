import sys
import asyncio
sys.path.insert(0, '.')
from api.portfolio import get_group_funds

async def test():
    # 测试交易测试组合（portfolio_id=2）
    result = await get_group_funds(2)
    if result['success']:
        print("交易测试组合 API 返回数据:")
        for fund in result['data']:
            cash = fund.get('available_cash')
            print(f"  {fund['fund_code']}: available_cash={cash}")
    else:
        print(f"Error: {result.get('message')}")

asyncio.run(test())
