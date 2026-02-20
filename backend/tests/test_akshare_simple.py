import akshare as ak

# 获取基金列表
print("正在获取基金列表...")
fund_df = ak.fund_name_em()
print(f"总基金数量: {len(fund_df)}")
print(f"\n字段名: {fund_df.columns.tolist()}")
print(f"\n前5条数据:")
print(fund_df.head(10).to_string())

# 使用"基金简称"字段进行筛选
name_col = '基金简称'

if name_col in fund_df.columns:
    print(f"\n使用字段 '{name_col}' 进行筛选")
    
    # 筛选永赢基金
    yongying = fund_df[fund_df[name_col].str.contains('永赢', na=False)]
    print(f"\n永赢基金数量: {len(yongying)}")
    if len(yongying) > 0:
        print("\n永赢基金列表（前20只）:")
        print(yongying.head(20).to_string(index=False))
    
    # 筛选中航基金
    zhonghang = fund_df[fund_df[name_col].str.contains('中航', na=False)]
    print(f"\n\n中航基金数量: {len(zhonghang)}")
    if len(zhonghang) > 0:
        print("\n中航基金列表（前20只）:")
        print(zhonghang.head(20).to_string(index=False))
else:
    print("未找到名称字段")

print("\n测试完成!")
