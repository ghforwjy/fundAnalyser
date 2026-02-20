"""
测试akshare获取基金净值的API - 第二版
"""
import akshare as ak
import pandas as pd

# 测试基金代码
test_funds = ['000330', '001052', '003003']

print("=" * 80)
print("测试akshare获取基金净值API - 第二版")
print("=" * 80)

for fund_code in test_funds:
    print(f"\n测试基金: {fund_code}")
    print("-" * 80)
    
    # 方法1: fund_open_fund_info_em (获取单位净值走势)
    print("\n方法1: fund_open_fund_info_em (单位净值走势)")
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  第一条: {df.iloc[0].to_dict()}")
            print(f"  最后一条: {df.iloc[-1].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)[:100]}")
    
    # 方法2: fund_open_fund_info_em (获取累计净值走势)
    print("\n方法2: fund_open_fund_info_em (累计净值走势)")
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="累计净值走势")
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  第一条: {df.iloc[0].to_dict()}")
            print(f"  最后一条: {df.iloc[-1].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)[:100]}")
    
    # 方法3: fund_open_fund_info_em (获取累计收益率走势)
    print("\n方法3: fund_open_fund_info_em (累计收益率走势)")
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="累计收益率走势")
        if df is not None and len(df) > 0:
            print(f"  成功! 数据条数: {len(df)}")
            print(f"  第一条: {df.iloc[0].to_dict()}")
            print(f"  最后一条: {df.iloc[-1].to_dict()}")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)[:100]}")
    
    # 方法4: fund_name_em - 获取基金列表（包含最新净值）
    print("\n方法4: fund_name_em")
    try:
        df = ak.fund_name_em()
        if df is not None and len(df) > 0:
            fund_data = df[df['基金代码'] == fund_code]
            if len(fund_data) > 0:
                print(f"  成功! 找到基金")
                print(f"  数据: {fund_data.iloc[0].to_dict()}")
            else:
                print(f"  失败: 未找到该基金")
        else:
            print(f"  失败: 无数据返回")
    except Exception as e:
        print(f"  失败: {str(e)[:100]}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
