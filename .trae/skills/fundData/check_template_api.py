"""
检查模板API返回的数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import list_take_profit_templates, get_take_profit_template

def check_template_api():
    """检查模板API返回的数据"""
    print("=" * 60)
    print("检查模板API返回的数据")
    print("=" * 60)

    # 获取所有模板
    templates = list_take_profit_templates()
    print(f"\n所有模板:")
    for t in templates:
        print(f"\n模板ID: {t['id']} - {t['name']}")
        print(f"  enable_buy_back: {t.get('enable_buy_back')} (类型: {type(t.get('enable_buy_back'))})")
        print(f"  buy_back_threshold: {t.get('buy_back_threshold')}")

    # 特别检查激进型模板（ID=2）
    print(f"\n" + "=" * 60)
    print(f"详细检查激进型模板（ID=2）:")
    template = get_take_profit_template(2)
    if template:
        for key, value in template.items():
            print(f"  {key}: {value} (类型: {type(value)})")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_template_api()
