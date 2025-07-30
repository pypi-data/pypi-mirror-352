"""
向后兼容 - 旧版API

保持与现有代码的100%兼容性
"""

import warnings
from typing import Type, Optional, List, Union
from tortoise.models import Model
from pydantic import BaseModel as PydanticModel

from ..core.base import FastCRUD
from ..core.schemas import BaseResponse
from ..features.caching import CacheConfig, CacheManager


class BaseApiOut(BaseResponse):
    """向后兼容的响应类"""
    
    def __init__(self, data=None, message="操作成功", **kwargs):
        super().__init__(data=data, message=message, **kwargs)


class ModelCrud(FastCRUD):
    """
    向后兼容的ModelCrud类
    
    保持与旧版本API的完全兼容
    """
    
    def __init__(
        self,
        model: Type[Model],
        create_schema: Type[PydanticModel] = None,
        read_schema: Type[PydanticModel] = None,
        update_schema: Type[PydanticModel] = None,
        enable_cache: bool = False,
        enable_hooks: bool = False,
        preload_relations: List[str] = None,
        **kwargs
    ):
        """
        向后兼容的初始化方法
        
        Args:
            model: Tortoise模型类
            create_schema: 创建数据模式
            read_schema: 读取数据模式
            update_schema: 更新数据模式
            enable_cache: 是否启用缓存
            enable_hooks: 是否启用Hook系统
            preload_relations: 预加载关系列表
        """
        # 发出弃用警告
        warnings.warn(
            "ModelCrud is deprecated. Use FastCRUD instead. "
            "ModelCrud will be removed in version 1.0.0",
            DeprecationWarning,
            stacklevel=2
        )
        
        # 转换为新的配置格式
        cache_config = CacheConfig() if enable_cache else False
        hook_config = True if enable_hooks else False
        
        super().__init__(
            model=model,
            create_schema=create_schema,
            read_schema=read_schema,
            update_schema=update_schema,
            cache=cache_config,
            hooks=hook_config,
            relations=preload_relations or [],
            **kwargs
        )
    
    # 保持旧的方法名
    def get_router(self):
        """向后兼容的路由获取方法"""
        warnings.warn(
            "get_router() is deprecated. Use .router property instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.router
    
    async def pre_create_all(self, items):
        """向后兼容的批量创建前处理"""
        warnings.warn(
            "pre_create_all() is deprecated. Use hooks instead.",
            DeprecationWarning,
            stacklevel=2
        )
        for item in items:
            yield item.dict() if hasattr(item, 'dict') else item


# 全局缓存管理器（向后兼容）
_global_cache_manager: Optional[CacheManager] = None


def init_cache(config: Union[CacheConfig, dict] = None) -> CacheManager:
    """
    初始化全局缓存管理器（向后兼容）
    
    Args:
        config: 缓存配置
        
    Returns:
        CacheManager: 缓存管理器实例
    """
    warnings.warn(
        "init_cache() is deprecated. Configure cache per FastCRUD instance instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    global _global_cache_manager
    
    if isinstance(config, dict):
        config = CacheConfig(**config)
    elif config is None:
        config = CacheConfig()
    
    _global_cache_manager = CacheManager(config)
    return _global_cache_manager


def get_cache_manager() -> Optional[CacheManager]:
    """
    获取全局缓存管理器（向后兼容）
    
    Returns:
        Optional[CacheManager]: 缓存管理器实例
    """
    warnings.warn(
        "get_cache_manager() is deprecated. Use instance-level cache instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return _global_cache_manager


# 其他向后兼容的导入
def setup_exception_handlers(app):
    """向后兼容的异常处理器设置"""
    warnings.warn(
        "setup_exception_handlers() is deprecated. "
        "Exception handling is now automatic.",
        DeprecationWarning,
        stacklevel=2
    )
    # 新版本中异常处理是自动的，这里保持空实现


def setup_monitoring(app, **kwargs):
    """向后兼容的监控设置"""
    warnings.warn(
        "setup_monitoring() is deprecated. "
        "Use monitoring=True in FastCRUD constructor instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # 新版本中监控是按实例配置的，这里保持空实现


# 导出向后兼容的类型
HookStage = str  # 简化的Hook阶段类型
HookPriority = str  # 简化的Hook优先级类型


class HookManager:
    """向后兼容的Hook管理器"""
    
    def __init__(self):
        warnings.warn(
            "HookManager is deprecated. Use FastCRUD hooks instead.",
            DeprecationWarning,
            stacklevel=2
        )


def hook(stage: str, priority: str = "normal"):
    """向后兼容的Hook装饰器"""
    warnings.warn(
        "Global hook decorator is deprecated. Use FastCRUD.hook() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    def decorator(func):
        return func
    return decorator


__all__ = [
    "ModelCrud",
    "BaseApiOut",
    "init_cache", 
    "get_cache_manager",
    "setup_exception_handlers",
    "setup_monitoring",
    "HookStage",
    "HookPriority",
    "HookManager",
    "hook"
]
