"""
测试波段捡回功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit import TakeProfitParams, TakeProfitCalculator
from take_profit_manager import TakeProfitTemplateManager

def test_buy_back_logic():
    """测试波段捡回逻辑"""
    print("=" * 60)
    print("测试波段捡回逻辑")
    print("=" * 60)

    # 创建启用波段捡回的参数
    params = TakeProfitParams(
        first_threshold=0.20,
        first_sell_ratio=0.30,
        step_size=0.05,
        follow_up_sell_ratio=0.20,
        enable_cost_control=True,
        target_diluted_cost=0.0,
        enable_buy_back=True,       # 启用波段捡回
        buy_back_threshold=0.20     # 20%捡回阈值
    )

    print(f"\n参数配置:")
    print(f"  启用波段捡回: {params.enable_buy_back}")
    print(f"  捡回阈值: {params.buy_back_threshold * 100}%")

    # 模拟未回收卖出记录
    unrecovered_sells = [
        {
            'id': 123,  # 目标卖出交易ID
            'shares': 1000,
            'confirmed_nav': 1.50,  # 卖出时净值1.50
            'nav': 1.50,
            'transaction_date': '2025-01-15'
        }
    ]

    calculator = TakeProfitCalculator(params)

    # 测试场景1: 当前净值1.20，跌幅20%，应该触发捡回
    print("\n场景1: 当前净值1.20，跌幅20%")
    action, sell_ratio, reason, buy_back_info = calculator._execute_logic(
        params=params,
        has_sell_record=True,
        current_profit_rate=0.10,
        current_nav=1.20,  # 当前净值1.20
        last_sell_nav=1.50,
        diluted_cost=1.0,
        available_cash=2000,  # 足够现金
        unrecovered_sells=unrecovered_sells
    )
    print(f"  结果: {action}")
    print(f"  原因: {reason}")
    if buy_back_info:
        print(f"  捡回份额: {buy_back_info['shares']}")
        print(f"  捡回金额: {buy_back_info['amount']:.2f}")
        print(f"  跌幅: {buy_back_info['decline_rate']*100:.2f}%")
        print(f"  目标交易ID: {buy_back_info['target_transaction_id']}")

    # 测试场景2: 当前净值1.30，跌幅13.3%，不触发捡回
    print("\n场景2: 当前净值1.30，跌幅13.3%（未达阈值）")
    action, sell_ratio, reason, buy_back_info = calculator._execute_logic(
        params=params,
        has_sell_record=True,
        current_profit_rate=0.10,
        current_nav=1.30,
        last_sell_nav=1.50,
        diluted_cost=1.0,
        available_cash=2000,
        unrecovered_sells=unrecovered_sells
    )
    print(f"  结果: {action}")
    print(f"  原因: {reason}")

    # 测试场景3: 现金不足
    print("\n场景3: 跌幅达标但现金不足")
    action, sell_ratio, reason, buy_back_info = calculator._execute_logic(
        params=params,
        has_sell_record=True,
        current_profit_rate=0.10,
        current_nav=1.20,
        last_sell_nav=1.50,
        diluted_cost=1.0,
        available_cash=500,  # 现金不足
        unrecovered_sells=unrecovered_sells
    )
    print(f"  结果: {action}")
    print(f"  原因: {reason}")

    # 测试场景4: 未启用波段捡回
    print("\n场景4: 未启用波段捡回")
    params_disabled = TakeProfitParams(
        first_threshold=0.20,
        first_sell_ratio=0.30,
        step_size=0.05,
        follow_up_sell_ratio=0.20,
        enable_cost_control=True,
        target_diluted_cost=0.0,
        enable_buy_back=False,  # 禁用波段捡回
        buy_back_threshold=0.20
    )
    calculator2 = TakeProfitCalculator(params_disabled)
    action, sell_ratio, reason, buy_back_info = calculator2._execute_logic(
        params=params_disabled,
        has_sell_record=True,
        current_profit_rate=0.10,
        current_nav=1.20,
        last_sell_nav=1.50,
        diluted_cost=1.0,
        available_cash=2000,
        unrecovered_sells=unrecovered_sells
    )
    print(f"  结果: {action}")
    print(f"  原因: {reason}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_template_manager():
    """测试模板管理器的波段捡回功能"""
    print("\n" + "=" * 60)
    print("测试模板管理器")
    print("=" * 60)

    manager = TakeProfitTemplateManager()

    # 创建带波段捡回的模板
    print("\n创建带波段捡回的模板...")
    result = manager.create_template(
        name='测试模板-波段捡回',
        description='测试波段捡回功能',
        first_threshold=0.20,
        first_sell_ratio=0.30,
        step_size=0.05,
        follow_up_sell_ratio=0.20,
        enable_cost_control=True,
        target_diluted_cost=0.0,
        enable_buy_back=True,
        buy_back_threshold=0.20
    )
    print(f"  创建结果: {result}")

    if result.get('success'):
        template_id = result['template_id']

        # 获取模板验证
        template = manager.get_template(template_id)
        print(f"\n  模板详情:")
        print(f"    名称: {template['name']}")
        print(f"    启用波段捡回: {template['enable_buy_back']}")
        print(f"    捡回阈值: {template['buy_back_threshold']}")

        # 更新模板
        print(f"\n  更新模板...")
        update_result = manager.update_template(
            template_id=template_id,
            buy_back_threshold=0.25
        )
        print(f"    更新结果: {update_result}")

        # 删除测试模板
        print(f"\n  删除测试模板...")
        delete_result = manager.delete_template(template_id)
        print(f"    删除结果: {delete_result}")

    print("\n" + "=" * 60)
    print("模板管理器测试完成")
    print("=" * 60)


def test_execute_buy_back():
    """测试执行捡回交易（需要真实组合数据）"""
    print("\n" + "=" * 60)
    print("测试执行捡回交易")
    print("=" * 60)

    from portfolio_manager import execute_buy_back_transaction, get_portfolio_transactions

    # 注意：这个测试需要真实的数据，这里只是演示接口
    print("\n执行捡回交易接口说明:")
    print("  函数: execute_buy_back_transaction()")
    print("  参数:")
    print("    - portfolio_id: 组合ID")
    print("    - fund_code: 基金代码")
    print("    - target_sell_transaction_id: 目标卖出交易ID")
    print("    - shares: 买入份额（必须与卖出份额一致）")
    print("    - amount: 买入金额")
    print("    - nav: 当前净值（可选）")
    print("  功能:")
    print("    1. 记录买入交易")
    print("    2. 标记卖出记录 is_recovered = 1")
    print("    3. 扣除组合现金")

    print("\n" + "=" * 60)
    print("执行捡回交易测试说明完成")
    print("=" * 60)


if __name__ == '__main__':
    test_buy_back_logic()
    test_template_manager()
    test_execute_buy_back()
