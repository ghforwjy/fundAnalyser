"""
检查基金的止盈配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit_manager import TakeProfitTemplateManager
from take_profit import TakeProfitCalculator, TakeProfitParams

def check_take_profit_config(portfolio_id=3, fund_code='021094'):
    """检查止盈配置"""
    print(f"=" * 70)
    print(f"检查组合 {portfolio_id} 基金 {fund_code} 的止盈配置")
    print(f"=" * 70)

    manager = TakeProfitTemplateManager()

    # 获取配置
    config = manager.get_fund_config(portfolio_id, fund_code)
    print(f"\n【配置详情】")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # 检查是否启用波段捡回
    print(f"\n【波段捡回设置】")
    print(f"  enable_buy_back: {config.get('enable_buy_back', False)}")
    print(f"  buy_back_threshold: {config.get('buy_back_threshold', 0.20)}")

    if not config.get('enable_buy_back', False):
        print(f"\n  ⚠️ 警告：波段捡回未启用！")
        print(f"  这是没有捡回建议的原因。")

    print(f"\n" + "=" * 70)

if __name__ == '__main__':
    check_take_profit_config(3, '021094')
