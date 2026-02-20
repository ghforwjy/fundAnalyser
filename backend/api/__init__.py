"""
API路由模块
"""
from .funds import router as funds_router
from .datasource import router as datasource_router
from .db_manage import router as db_manage_router
from .filters import router as filters_router
from .portfolio import router as portfolio_router

__all__ = [
    'funds_router',
    'datasource_router',
    'db_manage_router',
    'filters_router',
    'portfolio_router'
]
