"""
测试更新模板
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit_manager import TakeProfitTemplateManager

def test_update_template():
    """测试更新模板"""
    print("=" * 60)
    print("测试更新模板 - 启用波段捡回")
    print("=" * 60)

    manager = TakeProfitTemplateManager()

    # 获取激进型模板
    template_id = 2  # 激进型模板ID
    template = manager.get_template(template_id)

    print(f"\n更新前:")
    print(f"  enable_buy_back: {template.get('enable_buy_back')}")
    print(f"  buy_back_threshold: {template.get('buy_back_threshold')}")

    # 更新模板 - 启用波段捡回
    print(f"\n执行更新...")
    result = manager.update_template(
        template_id=template_id,
        enable_buy_back=True,
        buy_back_threshold=0.20
    )
    print(f"  更新结果: {result}")

    # 重新获取模板
    template = manager.get_template(template_id)
    print(f"\n更新后:")
    print(f"  enable_buy_back: {template.get('enable_buy_back')}")
    print(f"  buy_back_threshold: {template.get('buy_back_threshold')}")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_update_template()
