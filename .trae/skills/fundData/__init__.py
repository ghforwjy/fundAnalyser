"""
fundData Skill - AKShare基金数据管理工具
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_fund_data import (
    query_funds_nav,
    get_fund_nav,
    get_fund_holdings,
    format_holdings_report,
    get_fund_risk_and_return,
    get_portfolio_funds_full,
    format_portfolio_report,
    get_value_averaging_report_text,
)

from risk_metrics_calculator import (
    calculate_fund_risk_metrics,
    calculate_portfolio_risk_metrics,
    compare_with_xueqiu,
)

from portfolio_manager import (
    create_portfolio,
    list_portfolios,
    add_funds_to_portfolio,
    get_portfolio_profit_loss_report,
)

from fund_data_skill import FundDataSkill

__all__ = [
    # 查询接口
    'query_funds_nav',
    'get_fund_nav',
    'get_fund_holdings',
    'format_holdings_report',
    'get_fund_risk_and_return',
    'get_portfolio_funds_full',
    'format_portfolio_report',
    'get_value_averaging_report_text',
    # 风险指标计算
    'calculate_fund_risk_metrics',
    'calculate_portfolio_risk_metrics',
    'compare_with_xueqiu',
    # 组合管理
    'create_portfolio',
    'list_portfolios',
    'add_funds_to_portfolio',
    'get_portfolio_profit_loss_report',
    # 主类
    'FundDataSkill',
]
