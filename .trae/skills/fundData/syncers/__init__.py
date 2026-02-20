"""
同步器模块
"""
from .global_syncers import (
    sync_fund_info,
    sync_fund_rating,
    sync_fund_manager,
    sync_fund_company,
    sync_fund_dividend,
    sync_fund_split,
    sync_all_global_data
)

from .group_syncers import (
    sync_group_nav,
    sync_group_holdings,
    sync_group_risk_metrics,
    sync_group_performance,
    sync_group_all_data
)

__all__ = [
    # 全局数据同步器
    'sync_fund_info',
    'sync_fund_rating',
    'sync_fund_manager',
    'sync_fund_company',
    'sync_fund_dividend',
    'sync_fund_split',
    'sync_all_global_data',
    # 分组数据同步器
    'sync_group_nav',
    'sync_group_holdings',
    'sync_group_risk_metrics',
    'sync_group_performance',
    'sync_group_all_data'
]
