"""
检查AKShare返回的风险指标数据
"""
import akshare as ak

fund_code = '159566'
print(f"=== 获取基金 {fund_code} 的风险指标 ===")

try:
    df = ak.fund_individual_analysis_xq(symbol=fund_code)
    print(f"数据:\n{df}")
    print(f"\n列名: {df.columns.tolist()}")
    print(f"\n数据条数: {len(df)}")
except Exception as e:
    print(f"错误: {e}")
