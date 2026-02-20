"""
验证基金信息是否正确
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

# 需要验证的基金代码
fund_codes = {
    '024389': '中航智选领航混合C',  # 原图片显示"中航智造机遇混合C"
    '014048': '银华鑫盛灵活配置混合(LOF)C',  # 原图片显示"A"类
    '501022': '银华鑫盛灵活配置混合(LOF)A',  # 检查A类是否存在
}

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

print("=" * 100)
print("基金信息验证")
print("=" * 100)

for code, expected_name in fund_codes.items():
    info = get_fund_info(code)
    if info:
        print(f"\n基金代码: {info['fund_code']}")
        print(f"预期名称: {expected_name}")
        print(f"实际名称: {info['fund_name']}")
        print(f"基金类型: {info['fund_type']}")
        if info['fund_name'] == expected_name:
            print("✅ 名称匹配正确")
        else:
            print("❌ 名称不匹配")
    else:
        print(f"\n❌ 基金代码 {code} 未找到")

# 搜索"中航智造机遇"相关基金
print("\n" + "=" * 100)
print("搜索 '中航智造机遇' 相关基金")
print("=" * 100)

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fund_code, fund_name, fund_type FROM fund_info WHERE fund_name LIKE ? LIMIT 10",
        ("%中航智%",)
    )
    rows = cursor.fetchall()
    if rows:
        print("找到相关基金:")
        for row in rows:
            print(f"  - {row['fund_code']}: {row['fund_name']} ({row['fund_type']})")
    else:
        print("未找到相关基金")

print("\n" + "=" * 100)
