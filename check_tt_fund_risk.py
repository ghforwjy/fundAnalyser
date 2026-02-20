"""
尝试从天天基金网获取风险指标
"""
import akshare as ak

fund_code = '159566'
print(f"=== 尝试获取基金 {fund_code} 的各种数据 ===")

# 尝试获取基金评级数据（可能包含风险指标）
try:
    print("\n--- 基金评级 ---")
    df = ak.fund_rating_all()
    fund_rating = df[df['基金代码'] == fund_code]
    if not fund_rating.empty:
        print(fund_rating)
    else:
        print("无评级数据")
except Exception as e:
    print(f"获取失败: {e}")

# 尝试获取基金概况
try:
    print("\n--- 基金概况 ---")
    df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="基金概况")
    print(df)
except Exception as e:
    print(f"获取失败: {e}")

# 尝试获取基金排名
try:
    print("\n--- 基金排名 ---")
    df = ak.fund_open_fund_rank_em(symbol="全部")
    fund_rank = df[df['基金代码'] == fund_code]
    if not fund_rank.empty:
        print(fund_rank)
    else:
        print("无排名数据")
except Exception as e:
    print(f"获取失败: {e}")
