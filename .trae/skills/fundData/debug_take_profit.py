"""
调试止盈建议计算
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from take_profit import TakeProfitCalculator, TakeProfitParams
from take_profit_manager import TakeProfitTemplateManager
from portfolio_manager import calculate_fund_available_cash, get_portfolio_transactions

def debug_take_profit_calculation(portfolio_id=3, fund_code='021094'):
    """调试止盈建议计算"""
    print("=" * 70)
    print(f"调试组合 {portfolio_id} 基金 {fund_code} 的止盈建议计算")
    print("=" * 70)

    manager = TakeProfitTemplateManager()

    # 1. 获取基金配置
    print(f"\n【基金配置】")
    config = manager.get_fund_config(portfolio_id, fund_code)
    for key, value in config.items():
        print(f"  {key}: {value}")

    # 2. 获取未回收卖出记录
    print(f"\n【未回收卖出记录】")
    sell_transactions = get_portfolio_transactions(
        portfolio_id,
        fund_code=fund_code,
        transaction_type='SELL'
    )
    unrecovered_sells = [t for t in sell_transactions if t.get('is_recovered', 0) == 0]
    print(f"  未回收卖出记录数: {len(unrecovered_sells)}")
    for sell in unrecovered_sells:
        print(f"    ID:{sell['id']} 份额:{sell['shares']} 金额:{sell['amount']} confirmed_nav:{sell.get('confirmed_nav')} nav:{sell.get('nav')}")

    # 3. 获取可用现金
    print(f"\n【可用现金】")
    cash_info = calculate_fund_available_cash(portfolio_id, fund_code)
    print(f"  {cash_info}")

    # 4. 构建参数
    params = TakeProfitParams(
        first_threshold=config['first_threshold'],
        first_sell_ratio=config['first_sell_ratio'],
        step_size=config['step_size'],
        follow_up_sell_ratio=config['follow_up_sell_ratio'],
        enable_cost_control=config['enable_cost_control'],
        target_diluted_cost=config['target_diluted_cost'],
        enable_buy_back=config.get('enable_buy_back', False),
        buy_back_threshold=config.get('buy_back_threshold', 0.20)
    )
    print(f"\n【止盈参数】")
    print(f"  enable_buy_back: {params.enable_buy_back}")
    print(f"  buy_back_threshold: {params.buy_back_threshold}")

    # 5. 手动执行捡回判断逻辑
    print(f"\n【手动执行捡回判断】")
    if params.enable_buy_back and unrecovered_sells:
        target_sell = unrecovered_sells[0]
        target_sell_nav = target_sell.get('confirmed_nav') or target_sell.get('nav')
        target_shares = target_sell.get('shares', 0)
        print(f"  目标卖出记录ID: {target_sell['id']}")
        print(f"  目标卖出净值: {target_sell_nav}")
        print(f"  目标卖出份额: {target_shares}")

        if target_sell_nav and target_sell_nav > 0:
            # 获取当前净值
            from funddb import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT unit_nav FROM fund_nav
                    WHERE fund_code = ?
                    ORDER BY nav_date DESC
                    LIMIT 1
                ''', (fund_code,))
                row = cursor.fetchone()
                current_nav = row['unit_nav'] if row else 0
                print(f"  当前净值: {current_nav}")

                # 计算跌幅
                decline_rate = (target_sell_nav - current_nav) / target_sell_nav
                print(f"  跌幅: {decline_rate*100:.2f}%")
                print(f"  捡回阈值: {params.buy_back_threshold*100:.2f}%")
                print(f"  是否触发捡回: {'是' if decline_rate >= params.buy_back_threshold else '否'}")

                # 检查现金
                available_cash = cash_info.get('available_cash', 0)
                buy_back_amount = target_shares * current_nav
                print(f"  可用现金: {available_cash}")
                print(f"  捡回所需金额: {buy_back_amount}")
                print(f"  现金是否充足: {'是' if available_cash >= buy_back_amount else '否'}")
        else:
            print(f"  错误: 无法获取卖出净值")
    else:
        print(f"  未执行捡回判断:")
        print(f"    enable_buy_back: {params.enable_buy_back}")
        print(f"    unrecovered_sells数量: {len(unrecovered_sells)}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    debug_take_profit_calculation(3, '021094')
