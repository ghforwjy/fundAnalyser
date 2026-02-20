"""
测试tushare fund_nav接口的不同调用方式
"""
import sqlite3
import tushare as ts

# 获取token
conn = sqlite3.connect('../fund.db')
cursor = conn.cursor()
cursor.execute("SELECT api_key FROM data_source_config WHERE source_name = 'tushare'")
row = cursor.fetchone()
token = row[0] if row else None
conn.close()

if not token:
    print("未找到tushare token")
    exit(1)

ts.set_token(token)
pro = ts.pro_api()

print("=" * 60)
print("测试1: 按基金代码获取（当前方式）")
print("=" * 60)
df1 = pro.fund_nav(ts_code='159103.OF', start_date='20260213', end_date='20260214')
print(f"返回记录数: {len(df1) if df1 is not None else 0}")
if df1 is not None and len(df1) > 0:
    print(df1.head())

print("\n" + "=" * 60)
print("测试2: 按日期获取（获取某天所有基金）")
print("=" * 60)
df2 = pro.fund_nav(nav_date='20260214')
print(f"返回记录数: {len(df2) if df2 is not None else 0}")
if df2 is not None and len(df2) > 0:
    print(df2.head())
    print(f"\n唯一基金数: {df2['ts_code'].nunique()}")

print("\n" + "=" * 60)
print("测试3: 只用日期范围（不指定ts_code和nav_date）")
print("=" * 60)
try:
    df3 = pro.fund_nav(start_date='20260213', end_date='20260214')
    print(f"返回记录数: {len(df3) if df3 is not None else 0}")
    if df3 is not None and len(df3) > 0:
        print(df3.head())
        print(f"\n唯一基金数: {df3['ts_code'].nunique()}")
except Exception as e:
    print(f"错误: {e}")
