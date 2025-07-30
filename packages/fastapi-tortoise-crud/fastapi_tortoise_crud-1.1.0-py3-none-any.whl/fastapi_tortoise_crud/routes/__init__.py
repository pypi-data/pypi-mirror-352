"""
路由系统模块

提供CRUD路由的自动生成和管理
"""

from .crud import CrudRoutes
from .factory import CrudRouteFactory

__all__ = [
    "CrudRoutes",
    "CrudRouteFactory"
]
