"""
测试akshare获取基金净值的API
"""
import akshare as ak
import pandas as pd

# 测试基金代码
test_funds = ['000330', '001052', '003003']

print("=" * 80)
print("测试akshare获取基金净值API")
print("=" * 80)

for fund_code in test_funds:
    print(f"\n测试基金: {fund_code}")
    print("-" * 80)
    
    # 方法1: fund_em_open_fund_info
    print("\n方法1: fund_em_open_fund_info")
    try:
        df = ak.fund_em_open_fund_info(fund=fund_code, indicator="单位净值走势")
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  最新数据: {df.iloc[-1].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)}")
    
    # 方法2: fund_em_daily
    print("\n方法2: fund_em_daily")
    try:
        df = ak.fund_em_daily(fund=fund_code)
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  最新数据: {df.iloc[0].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)}")
    
    # 方法3: fund_open_fund_info_em (原来的方法)
    print("\n方法3: fund_open_fund_info_em")
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  最新数据: {df.iloc[0].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)}")
    
    # 方法4: fund_new_em
    print("\n方法4: fund_new_em")
    try:
        df = ak.fund_new_em()
        if df is not None and len(df) > 0:
            # 查找指定基金
            fund_data = df[df['基金代码'] == fund_code]
            if len(fund_data) > 0:
                print(f"  成功! 找到基金数据")
                print(f"  数据: {fund_data.iloc[0].to_dict()}")
            else:
                print(f"  失败: 未找到该基金")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
