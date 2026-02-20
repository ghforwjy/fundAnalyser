"""
测试tushare fund_div接口的不同调用方式
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
print("测试1: 按公告日期获取（ann_date）")
print("=" * 60)
try:
    df1 = pro.fund_div(ann_date='20240115')
    print(f"返回记录数: {len(df1) if df1 is not None else 0}")
    if df1 is not None and len(df1) > 0:
        print(df1.head())
        print(f"\n列名: {df1.columns.tolist()}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试2: 按除息日期获取（ex_date）")
print("=" * 60)
try:
    df2 = pro.fund_div(ex_date='20240116')
    print(f"返回记录数: {len(df2) if df2 is not None else 0}")
    if df2 is not None and len(df2) > 0:
        print(df2.head())
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试3: 按派息日期获取（pay_date）")
print("=" * 60)
try:
    df3 = pro.fund_div(pay_date='20240118')
    print(f"返回记录数: {len(df3) if df3 is not None else 0}")
    if df3 is not None and len(df3) > 0:
        print(df3.head())
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试4: 按基金代码获取（ts_code）")
print("=" * 60)
try:
    df4 = pro.fund_div(ts_code='000001.OF')
    print(f"返回记录数: {len(df4) if df4 is not None else 0}")
    if df4 is not None and len(df4) > 0:
        print(df4.head())
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试5: 尝试使用start_date和end_date")
print("=" * 60)
try:
    df5 = pro.fund_div(start_date='20240101', end_date='20241231')
    print(f"返回记录数: {len(df5) if df5 is not None else 0}")
    if df5 is not None and len(df5) > 0:
        print(df5.head())
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试6: 获取最近一年的数据（遍历公告日期）")
print("=" * 60)
# 获取2024年的数据，需要遍历公告日期
from datetime import datetime, timedelta

current_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
total_records = 0

while current_date <= end_date:
    date_str = current_date.strftime('%Y%m%d')
    try:
        df = pro.fund_div(ann_date=date_str)
        if df is not None and len(df) > 0:
            total_records += len(df)
            print(f"{date_str}: {len(df)}条记录")
    except Exception as e:
        pass
    
    current_date += timedelta(days=1)
    # 每10天输出一次进度
    if current_date.day == 1 or current_date == end_date:
        print(f"进度: {date_str}, 累计: {total_records}条")

print(f"\n2024年总计: {total_records}条分红记录")
