"""
查询最后两个基金信息
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

# 需要查询的基金代码
fund_codes = ['160514', '004011']

def get_fund_info(fund_code):
    """获取基金信息"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fund_code, fund_name, fund_type FROM fund_info WHERE fund_code = ?",
            (fund_code,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'fund_code': row['fund_code'],
                'fund_name': row['fund_name'],
                'fund_type': row['fund_type']
            }
        return None

print("=" * 80)
print("最后两个基金信息查询")
print("=" * 80)

for code in fund_codes:
    info = get_fund_info(code)
    if info:
        print(f"\n✅ 基金代码: {info['fund_code']}")
        print(f"   基金名称: {info['fund_name']}")
        print(f"   基金类型: {info['fund_type']}")
    else:
        print(f"\n❌ 基金代码 {code} 在数据库中未找到")

print("\n" + "=" * 80)
