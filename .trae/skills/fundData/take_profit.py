"""
止盈算法模块

核心逻辑：
1. 初次止盈：收益率 >= 首次止盈阈值 -> 卖出首次止盈比例
2. 后续止盈：较上次卖出净值涨幅 >= 阶梯步长 -> 卖出后续止盈比例
3. 成本控制：摊薄成本 <= 目标摊薄成本 -> 停止止盈
4. 可用现金限制：实际卖出金额不能超过可用现金

数据获取：
- 当前净值：get_fund_nav(fund_code) - 自动检查新鲜度
- 持仓信息：list_portfolio_funds(portfolio_id)
- 卖出记录：get_portfolio_transactions(portfolio_id, fund_code, transaction_type='SELL')
- 可用现金：calculate_portfolio_available_cash_batch(portfolio_id) - 批量预计算
"""

import sys
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection


@dataclass
class TakeProfitParams:
    first_threshold: float = 0.20
    first_sell_ratio: float = 0.30
    step_size: float = 0.05
    follow_up_sell_ratio: float = 0.20
    enable_cost_control: bool = True
    target_diluted_cost: float = 0.0
    enable_buy_back: bool = False       # 是否启用波段捡回（高抛低吸）
    buy_back_threshold: float = 0.20    # 捡回阈值（如0.20表示下跌20%触发）


@dataclass
class TakeProfitFundResult:
    fund_code: str
    fund_name: str
    current_shares: float
    current_nav: float
    current_value: float
    buy_nav: float
    current_profit_rate: float
    has_sell_record: bool
    last_sell_nav: Optional[float]
    last_sell_date: Optional[str]
    diluted_cost: Optional[float]
    available_cash: float                    # 可用现金（仅显示，不限制卖出）
    action: str                              # SELL / HOLD / STOP / BUY / ERROR
    sell_ratio: Optional[float]
    sell_shares: Optional[float]
    sell_amount: Optional[float]             # 卖出金额
    reason: str
    param_source: str
    template_name: Optional[str]
    algorithm_details: List[str] = field(default_factory=list)
    
    # 波段捡回专属字段
    buy_back_shares: Optional[float] = None    # 建议买回的份额
    buy_back_amount: Optional[float] = None    # 预计花费金额
    unrecovered_sells_count: int = 0           # 剩余未回收的卖出笔数
    target_sell_nav: Optional[float] = None    # 目标卖出净值（用于计算跌幅）
    decline_rate: Optional[float] = None       # 当前跌幅


class TakeProfitCalculator:
    
    def __init__(self, params: TakeProfitParams = None):
        self.params = params or TakeProfitParams()
    
    def calculate(self, fund_code: str, portfolio_id: int, 
                  available_cash: float = 0,                     # 预计算的可用现金
                  params: TakeProfitParams = None,
                  param_source: str = 'default',
                  template_name: str = None) -> TakeProfitFundResult:
        from smart_fund_data import get_fund_nav
        from portfolio_manager import list_portfolio_funds, get_portfolio_transactions
        
        use_params = params or self.params
        details = []
        
        details.append(f"【算法入参】")
        details.append(f"基金代码: {fund_code}")
        details.append(f"组合ID: {portfolio_id}")
        details.append(f"可用现金: {available_cash:.2f}")
        details.append(f"首次止盈阈值: {use_params.first_threshold * 100}%")
        details.append(f"首次止盈卖出比例: {use_params.first_sell_ratio * 100}%")
        details.append(f"阶梯步长: {use_params.step_size * 100}%")
        details.append(f"后续止盈卖出比例: {use_params.follow_up_sell_ratio * 100}%")
        details.append(f"启用成本控制: {use_params.enable_cost_control}")
        details.append(f"目标摊薄成本: {use_params.target_diluted_cost}")
        details.append(f"启用波段捡回: {use_params.enable_buy_back}")
        details.append(f"捡回阈值: {use_params.buy_back_threshold * 100}%")
        details.append(f"参数来源: {param_source}")
        if template_name:
            details.append(f"使用模板: {template_name}")
        details.append("")
        
        details.append(f"【数据获取】")
        
        nav_data = get_fund_nav(fund_code, force_update=False)
        if not nav_data:
            return self._error_result(fund_code, available_cash, "无法获取净值数据", details)
        
        current_nav = nav_data.get('unit_nav', 0)
        nav_date = nav_data.get('nav_date', '')
        details.append(f"当前净值: {current_nav} ({nav_date})")
        
        funds = list_portfolio_funds(portfolio_id)
        fund_holding = None
        for f in funds:
            if f['fund_code'] == fund_code:
                fund_holding = f
                break
        
        if not fund_holding:
            return self._error_result(fund_code, available_cash, "该基金不在组合中", details)
        
        current_shares = fund_holding.get('shares', 0) or 0
        buy_nav = fund_holding.get('buy_nav', 0) or 0
        cost_nav = fund_holding.get('cost_nav', 0) or 0
        fund_name = fund_holding.get('fund_name', '')
        
        details.append(f"当前份额: {current_shares}")
        details.append(f"买入净值: {buy_nav}")
        details.append(f"摊薄成本净值: {cost_nav}")
        details.append(f"基金名称: {fund_name}")
        
        current_value = current_shares * current_nav
        current_profit_rate = (current_nav - buy_nav) / buy_nav if buy_nav > 0 else 0
        
        details.append(f"当前市值: {current_value:.2f}")
        details.append(f"当前收益率: {current_profit_rate * 100:.2f}%")
        details.append("")
        
        sell_transactions = get_portfolio_transactions(
            portfolio_id,
            fund_code=fund_code,
            transaction_type='SELL'
        )

        # 筛选未回收的卖出记录（用于波段捡回）
        unrecovered_sells = [t for t in sell_transactions if t.get('is_recovered', 0) == 0]
        unrecovered_sells_count = len(unrecovered_sells)

        has_sell_record = len(sell_transactions) > 0
        last_sell_nav = None
        last_sell_date = None

        if has_sell_record:
            last_sell = sell_transactions[0]
            last_sell_nav = last_sell.get('nav')
            last_sell_date = last_sell.get('transaction_date')
            details.append(f"最近卖出记录: {last_sell_date}, 净值: {last_sell_nav}")
            details.append(f"未回收卖出记录: {unrecovered_sells_count} 笔")
        else:
            details.append(f"卖出记录: 无")
        details.append("")
        
        # 执行止盈/捡回判断逻辑
        action, sell_ratio, reason, buy_back_info = self._execute_logic(
            use_params, has_sell_record, current_profit_rate,
            current_nav, last_sell_nav, cost_nav, available_cash,
            unrecovered_sells
        )

        details.append(f"【止盈判断】")
        details.append(f"判断结果: {action}")
        details.append(f"判断原因: {reason}")

        # 计算卖出金额（止盈卖出不考虑可用现金限制）
        sell_shares = None
        sell_amount = None
        buy_back_shares = None
        buy_back_amount = None
        target_sell_nav = None
        decline_rate = None
        target_transaction_id = None

        if action == 'SELL' and sell_ratio:
            sell_shares = current_shares * sell_ratio
            sell_amount = sell_shares * current_nav

            details.append(f"卖出份额: {sell_shares:.2f}")
            details.append(f"卖出金额: {sell_amount:.2f}")
        elif action == 'BUY' and buy_back_info:
            buy_back_shares = buy_back_info.get('shares')
            buy_back_amount = buy_back_info.get('amount')
            target_sell_nav = buy_back_info.get('target_sell_nav')
            decline_rate = buy_back_info.get('decline_rate')
            target_transaction_id = buy_back_info.get('target_transaction_id')

            details.append(f"捡回份额: {buy_back_shares:.2f}")
            details.append(f"捡回金额: {buy_back_amount:.2f}")
            details.append(f"目标卖出净值: {target_sell_nav:.4f}")
            details.append(f"当前跌幅: {decline_rate * 100:.2f}%")
            if target_transaction_id:
                details.append(f"目标卖出记录ID: {target_transaction_id}")

        return TakeProfitFundResult(
            fund_code=fund_code,
            fund_name=fund_name,
            current_shares=current_shares,
            current_nav=current_nav,
            current_value=current_value,
            buy_nav=buy_nav,
            current_profit_rate=current_profit_rate,
            has_sell_record=has_sell_record,
            last_sell_nav=last_sell_nav,
            last_sell_date=last_sell_date,
            diluted_cost=cost_nav,
            available_cash=available_cash,
            action=action,
            sell_ratio=sell_ratio,
            sell_shares=sell_shares,
            sell_amount=sell_amount,
            reason=reason,
            param_source=param_source,
            template_name=template_name,
            algorithm_details=details,
            buy_back_shares=buy_back_shares,
            buy_back_amount=buy_back_amount,
            unrecovered_sells_count=unrecovered_sells_count,
            target_sell_nav=target_sell_nav,
            decline_rate=decline_rate
        )
    
    def _execute_logic(self, params: TakeProfitParams, has_sell_record: bool,
                       current_profit_rate: float, current_nav: float,
                       last_sell_nav: Optional[float], diluted_cost: float,
                       available_cash: float,
                       unrecovered_sells: List[Dict[str, Any]]) -> tuple:
        """
        执行止盈/捡回判断逻辑

        返回: (action, sell_ratio, reason, buy_back_info)
        - action: 'SELL' / 'HOLD' / 'STOP' / 'BUY'
        - sell_ratio: 卖出比例（仅SELL时有效）
        - reason: 判断原因说明
        - buy_back_info: 捡回信息字典（仅BUY时有效）
        """
        # 1. 成本控制检查
        if params.enable_cost_control:
            if diluted_cost <= params.target_diluted_cost:
                return 'STOP', None, f"摊薄成本({diluted_cost:.4f}) <= 目标成本({params.target_diluted_cost})，本金已收回，停止止盈", None

        # 2. 波段捡回检查（优先于后续止盈）
        # 条件：启用波段捡回、有未回收卖出记录
        if params.enable_buy_back and unrecovered_sells:
            # 按时间倒序取最近一笔未回收卖出记录（LIFO原则）
            target_sell = unrecovered_sells[0]
            target_sell_nav = target_sell.get('confirmed_nav') or target_sell.get('nav')
            target_shares = target_sell.get('shares', 0)

            if target_sell_nav and target_sell_nav > 0:
                # 计算跌幅 = (卖出净值 - 当前净值) / 卖出净值
                decline_rate = (target_sell_nav - current_nav) / target_sell_nav

                if decline_rate >= params.buy_back_threshold:
                    # 跌幅达标，检查现金是否充足
                    buy_back_amount = target_shares * current_nav

                    if available_cash >= buy_back_amount:
                        buy_back_info = {
                            'shares': target_shares,
                            'amount': buy_back_amount,
                            'target_sell_nav': target_sell_nav,
                            'decline_rate': decline_rate,
                            'target_transaction_id': target_sell.get('id')
                        }
                        return 'BUY', None, \
                            f"波段捡回触发：跌幅({decline_rate*100:.2f}%) >= 捡回阈值({params.buy_back_threshold*100}%)，建议买回{target_shares:.2f}份", \
                            buy_back_info
                    else:
                        return 'HOLD', None, \
                            f"跌幅({decline_rate*100:.2f}%) >= 捡回阈值，但可用现金({available_cash:.2f})不足({buy_back_amount:.2f})，无法捡回", None

        # 3. 初次止盈判断
        if not has_sell_record:
            if current_profit_rate >= params.first_threshold:
                return 'SELL', params.first_sell_ratio, \
                    f"初次止盈触发：收益率({current_profit_rate*100:.2f}%) >= 首次止盈阈值({params.first_threshold*100}%)", None
            else:
                return 'HOLD', None, \
                    f"收益率({current_profit_rate*100:.2f}%) < 首次止盈阈值({params.first_threshold*100}%)，继续持有", None
        else:
            # 4. 后续止盈判断
            if last_sell_nav is None or last_sell_nav <= 0:
                return 'HOLD', None, "无法获取上次卖出净值", None

            increase_rate = (current_nav - last_sell_nav) / last_sell_nav

            if increase_rate >= params.step_size:
                return 'SELL', params.follow_up_sell_ratio, \
                    f"后续止盈触发：净值涨幅({increase_rate*100:.2f}%) >= 阶梯步长({params.step_size*100}%)", None
            else:
                return 'HOLD', None, \
                    f"净值涨幅({increase_rate*100:.2f}%) < 阶梯步长({params.step_size*100}%)，继续持有", None
    
    def _error_result(self, fund_code: str, available_cash: float, error_msg: str,
                      details: List[str]) -> TakeProfitFundResult:
        details.append(f"错误: {error_msg}")
        return TakeProfitFundResult(
            fund_code=fund_code,
            fund_name='',
            current_shares=0,
            current_nav=0,
            current_value=0,
            buy_nav=0,
            current_profit_rate=0,
            has_sell_record=False,
            last_sell_nav=None,
            last_sell_date=None,
            diluted_cost=None,
            available_cash=available_cash,
            action='ERROR',
            sell_ratio=None,
            sell_shares=None,
            sell_amount=None,
            reason=error_msg,
            param_source='error',
            template_name=None,
            algorithm_details=details,
            buy_back_shares=None,
            buy_back_amount=None,
            unrecovered_sells_count=0,
            target_sell_nav=None,
            decline_rate=None
        )
    
    def calculate_portfolio(self, portfolio_id: int) -> Dict[str, Any]:
        from portfolio_manager import list_portfolio_funds, calculate_portfolio_available_cash_batch
        from take_profit_manager import TakeProfitTemplateManager

        template_manager = TakeProfitTemplateManager()
        funds = list_portfolio_funds(portfolio_id)

        # 【批量预计算】一次性计算所有基金的可用现金
        available_cash_map = calculate_portfolio_available_cash_batch(portfolio_id)

        results = []
        for fund in funds:
            fund_code = fund['fund_code']

            # 获取预计算的可用现金
            available_cash = available_cash_map.get(fund_code, 0)

            config = template_manager.get_fund_config(portfolio_id, fund_code)
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

            result = self.calculate(
                fund_code, portfolio_id,
                available_cash=available_cash,  # 传入预计算的可用现金
                params=params,
                param_source=config.get('param_source', 'default'),
                template_name=config.get('template_name')
            )
            results.append(result)

        return {
            'portfolio_id': portfolio_id,
            'mode': 'ladder',
            'mode_name': '阶梯止盈法',
            'params': {
                'first_threshold': self.params.first_threshold,
                'first_sell_ratio': self.params.first_sell_ratio,
                'step_size': self.params.step_size,
                'follow_up_sell_ratio': self.params.follow_up_sell_ratio,
                'enable_cost_control': self.params.enable_cost_control,
                'target_diluted_cost': self.params.target_diluted_cost,
                'enable_buy_back': self.params.enable_buy_back,
                'buy_back_threshold': self.params.buy_back_threshold
            },
            'funds': [asdict(r) for r in results],
            'summary': {
                'total_funds': len(results),
                'need_action_count': sum(1 for r in results if r.action == 'SELL'),
                'hold_count': sum(1 for r in results if r.action == 'HOLD'),
                'stop_count': sum(1 for r in results if r.action == 'STOP'),
                'buy_back_count': sum(1 for r in results if r.action == 'BUY'),
                'error_count': sum(1 for r in results if r.action == 'ERROR'),
                'total_sell_amount': sum(r.sell_amount or 0 for r in results if r.action == 'SELL'),
                'total_buy_back_amount': sum(r.buy_back_amount or 0 for r in results if r.action == 'BUY')
            }
        }


def calculate_take_profit(fund_code: str, portfolio_id: int, 
                          available_cash: float = 0,
                          params: TakeProfitParams = None) -> TakeProfitFundResult:
    calc = TakeProfitCalculator(params)
    return calc.calculate(fund_code, portfolio_id, available_cash, params)


def calculate_portfolio_take_profit(portfolio_id: int) -> Dict[str, Any]:
    calc = TakeProfitCalculator()
    return calc.calculate_portfolio(portfolio_id)


def get_take_profit_report_text(portfolio_id: int) -> str:
    result = calculate_portfolio_take_profit(portfolio_id)

    lines = []
    lines.append("=" * 80)
    lines.append(f"止盈建议报告 - 组合ID: {result['portfolio_id']}")
    lines.append(f"策略: {result['mode_name']}")
    lines.append("=" * 80)

    for fund in result['funds']:
        lines.append(f"\n{fund['fund_code']} {fund['fund_name']}")
        lines.append(f"  当前份额: {fund['current_shares']:.2f}")
        lines.append(f"  当前净值: {fund['current_nav']:.4f}")
        lines.append(f"  当前市值: {fund['current_value']:.2f}")
        lines.append(f"  当前收益率: {fund['current_profit_rate']*100:.2f}%")
        lines.append(f"  可用现金: {fund['available_cash']:.2f}")
        lines.append(f"  操作建议: {fund['action']}")
        if fund['action'] == 'SELL':
            lines.append(f"  卖出金额: {fund['sell_amount']:.2f}元")
        elif fund['action'] == 'BUY':
            lines.append(f"  捡回份额: {fund['buy_back_shares']:.2f}份")
            lines.append(f"  捡回金额: {fund['buy_back_amount']:.2f}元")
            lines.append(f"  目标卖出净值: {fund['target_sell_nav']:.4f}")
            lines.append(f"  当前跌幅: {fund['decline_rate']*100:.2f}%")
        lines.append(f"  原因: {fund['reason']}")

    lines.append("\n" + "-" * 80)
    lines.append(f"汇总: 共{result['summary']['total_funds']}只基金")
    lines.append(f"  建议卖出: {result['summary']['need_action_count']}只")
    lines.append(f"  建议捡回: {result['summary'].get('buy_back_count', 0)}只")
    lines.append(f"  继续持有: {result['summary']['hold_count']}只")
    lines.append(f"  停止止盈: {result['summary']['stop_count']}只")
    lines.append(f"  预计卖出金额: {result['summary']['total_sell_amount']:.2f}元")
    lines.append(f"  预计捡回金额: {result['summary'].get('total_buy_back_amount', 0):.2f}元")
    lines.append("=" * 80)

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_take_profit_report_text(1))
