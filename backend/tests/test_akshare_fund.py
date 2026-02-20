"""
测试 AKShare 基金数据查询
查询永赢基金和中航基金的产品
"""
import akshare as ak
import pandas as pd
import sys

# 重定向输出到文件
output_file = open('tests/test_akshare_output.txt', 'w', encoding='utf-8')
sys.stdout = output_file

def test_fund_list():
    """测试获取基金列表并筛选永赢和中航基金"""
    print("=" * 60)
    print("正在获取基金列表...")
    print("=" * 60)
    
    # 获取所有基金列表
    fund_df = ak.fund_name_em()
    print(f"\n总基金数量: {len(fund_df)}")
    print(f"\n基金列表字段: {fund_df.columns.tolist()}")
    print(f"\n前5条数据预览:")
    print(fund_df.head())
    
    # 筛选永赢基金
    yongying_funds = fund_df[fund_df['名称'].str.contains('永赢', na=False)]
    print(f"\n" + "=" * 60)
    print(f"永赢基金产品数量: {len(yongying_funds)}")
    print("=" * 60)
    if len(yongying_funds) > 0:
        print(yongying_funds.to_string())
    
    # 筛选中航基金
    zhonghang_funds = fund_df[fund_df['名称'].str.contains('中航', na=False)]
    print(f"\n" + "=" * 60)
    print(f"中航基金产品数量: {len(zhonghang_funds)}")
    print("=" * 60)
    if len(zhonghang_funds) > 0:
        print(zhonghang_funds.to_string())
    
    return fund_df, yongying_funds, zhonghang_funds

def test_fund_daily():
    """测试获取开放式基金每日净值"""
    print("\n" + "=" * 60)
    print("正在获取开放式基金每日净值...")
    print("=" * 60)
    
    try:
        daily_df = ak.fund_open_fund_daily_em()
        print(f"\n当日净值数据数量: {len(daily_df)}")
        print(f"\n字段: {daily_df.columns.tolist()}")
        print(f"\n前5条数据:")
        print(daily_df.head())
        
        # 筛选永赢基金
        yongying_daily = daily_df[daily_df['基金名称'].str.contains('永赢', na=False)]
        print(f"\n当日永赢基金数量: {len(yongying_daily)}")
        if len(yongying_daily) > 0:
            print(yongying_daily[['基金代码', '基金名称', '单位净值', '累计净值', '日增长率']].to_string())
        
        # 筛选中航基金
        zhonghang_daily = daily_df[daily_df['基金名称'].str.contains('中航', na=False)]
        print(f"\n当日中航基金数量: {len(zhonghang_daily)}")
        if len(zhonghang_daily) > 0:
            print(zhonghang_daily[['基金代码', '基金名称', '单位净值', '累计净值', '日增长率']].to_string())
        
        return daily_df
    except Exception as e:
        print(f"获取每日净值失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_fund_info(fund_code: str):
    """测试获取单只基金详细信息"""
    print(f"\n" + "=" * 60)
    print(f"正在获取基金 {fund_code} 的详细信息...")
    print("=" * 60)
    
    try:
        # 获取单位净值走势
        nav_trend = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        print(f"\n单位净值走势 (最近10条):")
        print(nav_trend.tail(10).to_string())
        
        # 获取累计净值走势
        accum_nav = ak.fund_open_fund_info_em(symbol=fund_code, indicator="累计净值走势")
        print(f"\n累计净值走势 (最近10条):")
        print(accum_nav.tail(10).to_string())
        
        return nav_trend
    except Exception as e:
        print(f"获取基金 {fund_code} 信息失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        # 1. 获取基金列表并筛选
        fund_df, yongying_funds, zhonghang_funds = test_fund_list()
        
        # 2. 获取每日净值
        daily_df = test_fund_daily()
        
        # 3. 如果有永赢基金，测试获取详细信息
        if len(yongying_funds) > 0:
            first_yongying_code = yongying_funds.iloc[0]['基金代码']
            print(f"\n\n测试获取永赢基金详情: {first_yongying_code}")
            test_fund_info(first_yongying_code)
        
        # 4. 如果有中航基金，测试获取详细信息
        if len(zhonghang_funds) > 0:
            first_zhonghang_code = zhonghang_funds.iloc[0]['基金代码']
            print(f"\n\n测试获取中航基金详情: {first_zhonghang_code}")
            test_fund_info(first_zhonghang_code)
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        output_file.close()
        sys.stdout = sys.__stdout__
        print("测试完成，结果已保存到 tests/test_akshare_output.txt")
