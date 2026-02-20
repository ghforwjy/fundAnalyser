import akshare as ak

# 测试获取单只基金的详细信息
print("=" * 80)
print("测试 fund_individual_basic_info_xq 接口 - 获取单只基金详细信息")
print("=" * 80)

try:
    df = ak.fund_individual_basic_info_xq(symbol="018956")
    print(f"\n基金 018956 的详细信息:")
    print(df.to_string())
except Exception as e:
    print(f"获取失败: {e}")

# 测试 fund_name_em 接口返回的字段
print("\n" + "=" * 80)
print("测试 fund_name_em 接口 - 获取基金列表")
print("=" * 80)

try:
    df = ak.fund_name_em()
    print(f"\n总基金数: {len(df)}")
    print(f"\n列名: {list(df.columns)}")
    print(f"\n前5条数据:")
    print(df.head().to_string())
    
    # 查找 018956
    fund_018956 = df[df['基金代码'] == '018956']
    if not fund_018956.empty:
        print(f"\n\n找到 018956:")
        print(fund_018956.to_string())
    else:
        print(f"\n\n未找到 018956")
except Exception as e:
    print(f"获取失败: {e}")

# 测试 fund_rating_all 接口
print("\n" + "=" * 80)
print("测试 fund_rating_all 接口 - 获取基金评级（含基金公司）")
print("=" * 80)

try:
    df = ak.fund_rating_all()
    print(f"\n总记录数: {len(df)}")
    print(f"\n列名: {list(df.columns)}")
    print(f"\n前5条数据:")
    print(df.head().to_string())
    
    # 查找 018956
    fund_018956 = df[df['代码'] == '018956']
    if not fund_018956.empty:
        print(f"\n\n找到 018956:")
        print(fund_018956.to_string())
    else:
        print(f"\n\n评级数据中未找到 018956")
except Exception as e:
    print(f"获取失败: {e}")
