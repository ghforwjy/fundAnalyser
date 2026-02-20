"""
查看AKShare提供的风险指标和业绩数据接口
"""
import akshare as ak
import pandas as pd

print("=" * 80)
print("AKShare 风险指标接口 - fund_individual_analysis_xq")
print("=" * 80)

try:
    # 获取单只基金的风险指标
    df_risk = ak.fund_individual_analysis_xq(symbol="000001")
    print(f"\n接口返回数据列: {list(df_risk.columns)}")
    print(f"\n数据示例:\n{df_risk}")
except Exception as e:
    print(f"获取失败: {e}")

print("\n" + "=" * 80)
print("AKShare 业绩表现接口 - fund_individual_achievement_xq")
print("=" * 80)

try:
    # 获取单只基金的业绩表现
    df_perf = ak.fund_individual_achievement_xq(symbol="000001")
    print(f"\n接口返回数据列: {list(df_perf.columns)}")
    print(f"\n数据示例:\n{df_perf}")
except Exception as e:
    print(f"获取失败: {e}")

print("\n" + "=" * 80)
print("AKShare 基金排行接口 - fund_open_fund_rank_em")
print("=" * 80)

try:
    # 获取基金排行（包含收益率数据）
    df_rank = ak.fund_open_fund_rank_em(symbol="全部")
    print(f"\n接口返回数据列: {list(df_rank.columns)}")
    print(f"\n前3条数据:\n{df_rank.head(3)}")
except Exception as e:
    print(f"获取失败: {e}")
