"""
FastAPI Tortoise CRUD - 重构版本

提供简洁、强大、易用的FastAPI + Tortoise ORM CRUD解决方案

主要特性：
- 🚀 快速CRUD操作
- 💾 智能缓存系统（内存/Redis）
- 🎣 灵活的Hook系统
- 📊 性能监控
- 🔗 自动关系处理
- 🛡️ 完善的异常处理
- 📚 自动API文档
"""

from .core.base import FastCRUD
from .core.models import BaseModel
from .core.schemas import BaseResponse, PaginatedResponse, PaginationParams
from .core.dependencies import DependencyConfig, EndpointType
from .core.types import CrudConfig
from .features.caching import CacheConfig, init_global_cache, get_global_cache_stats
from .features.hooks import HookConfig, HookStage, HookContext
from .core.status_codes import StatusCode, Status
from .features.monitoring import MonitoringConfig
from .utils.exceptions import CrudException, ValidationError, NotFoundError

# 向后兼容导入
from .compatibility.legacy import ModelCrud

__version__ = "0.4.0"

__all__ = [
    # 主要API
    "FastCRUD",
    "BaseModel",
    "BaseResponse",
    "PaginatedResponse",
    "PaginationParams",

    # 配置类
    "CrudConfig",
    "CacheConfig",
    "MonitoringConfig",
    "DependencyConfig",
    "EndpointType",
    "HookConfig",
    "HookStage",
    "HookContext",
    "StatusCode",
    "Status",

    # 缓存管理
    "init_global_cache",
    "get_global_cache_stats",

    # Hook系统 (通过FastCRUD实例的hook方法使用)

    # 异常类
    "CrudException",
    "ValidationError",
    "NotFoundError",

    # 向后兼容
    "ModelCrud",
]

# 版本信息
__author__ = "FastAPI Tortoise CRUD Team"
__email__ = "support@fastapi-tortoise-crud.com"
__license__ = "MIT"
__description__ = "FastAPI + Tortoise ORM CRUD solution with caching, hooks, and monitoring"

def get_version():
    """获取版本信息"""
    return __version__

def get_info():
    """获取库信息"""
    return {
        "name": "fastapi-tortoise-crud",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "features": [
            "Fast CRUD operations",
            "Smart caching (Memory/Redis)",
            "Flexible hook system", 
            "Performance monitoring",
            "Automatic relationship handling",
            "Comprehensive exception handling",
            "Auto-generated API documentation"
        ]
    }
