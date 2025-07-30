"""
FastCRUD - 核心CRUD类

提供简洁、强大的CRUD操作接口
"""

from typing import Type, Optional, List, Union, Dict, Any
from fastapi import APIRouter, Depends
from tortoise.models import Model
from pydantic import BaseModel as PydanticModel

from .dependencies import DependencyConfig
from .types import CrudConfig
from .schemas import BaseResponse, PaginatedResponse
from ..features.caching import CacheConfig, get_cache_manager
from ..features.hooks import HookManager, HookConfig
from ..features.monitoring import MonitoringConfig, MonitoringManager
from ..routes.factory import CrudRouteFactory
from ..utils.exceptions import ValidationError


class FastCRUD:
    """
    FastCRUD - 主要的CRUD类
    
    提供简洁的API来创建完整的CRUD操作
    """
    
    def __init__(
        self,
        model: Type[Model],
        *,
        # 基础配置
        prefix: str = None,
        tags: List[str] = None,
        
        # Schema配置
        create_schema: Type[PydanticModel] = None,
        read_schema: Type[PydanticModel] = None,
        update_schema: Type[PydanticModel] = None,
        
        # 功能开关
        cache: Union[bool, CacheConfig] = False,
        hooks: Union[bool, HookConfig] = False,
        monitoring: Union[bool, MonitoringConfig] = False,
        
        # 关系配置
        relations: List[str] = None,
        
        # 查询配置
        text_contains_search: bool = True,

        # 调试配置
        debug_mode: bool = False,

        # 其他配置
        dependencies: Union[List[Depends], "DependencyConfig"] = None,
        **kwargs
    ):
        """
        初始化FastCRUD

        Args:
            model: Tortoise模型类
            prefix: 路由前缀
            tags: API标签
            create_schema: 创建数据模式
            read_schema: 读取数据模式
            update_schema: 更新数据模式
            cache: 缓存配置
            hooks: Hook配置
            monitoring: 监控配置
            relations: 关系字段列表
            text_contains_search: 文本字段是否使用包含查询
            debug_mode: 调试模式，控制详细日志输出
            dependencies: 依赖注入列表
            **kwargs: 其他配置参数，包括缓存覆盖参数
        """
        self.model = model

        # 分离缓存覆盖参数
        cache_override_keys = {
            'default_ttl', 'backend', 'max_memory_items', 'redis_url',
            'redis_pool_size', 'redis_timeout', 'serializer', 'key_prefix',
            'enable_compression', 'compression_threshold', 'cache_null_values',
            'null_value_ttl', 'enable_metrics', 'metrics_interval'
        }
        cache_overrides = {k: v for k, v in kwargs.items() if k in cache_override_keys}
        other_kwargs = {k: v for k, v in kwargs.items() if k not in cache_override_keys}

        self.config = CrudConfig(
            prefix=prefix if prefix is not None else f"/{model.__name__.lower()}",
            tags=tags if tags is not None else [model.__name__],  # 只有当tags为None时才使用默认值
            create_schema=create_schema,
            read_schema=read_schema,
            update_schema=update_schema,
            relations=relations or [],
            text_contains_search=text_contains_search,
            debug_mode=debug_mode,
            dependencies=dependencies or [],
            **other_kwargs
        )

        # 初始化功能管理器
        self._init_cache(cache, cache_overrides)
        self._init_hooks(hooks)
        self._init_monitoring(monitoring)
        
        # 创建路由
        self._router = self._create_router()
    
    def _init_cache(self, cache_config: Union[bool, CacheConfig], cache_overrides: dict = None):
        """初始化缓存"""
        cache_overrides = cache_overrides or {}

        if cache_config is False:
            self.cache_manager = None
        elif cache_config is True:
            # 使用全局配置 + 覆盖参数
            self.cache_manager = get_cache_manager(
                instance_id=f"{self.model.__name__}_default",
                **cache_overrides
            )
        else:
            # 使用实例配置（优先级最高）
            self.cache_manager = get_cache_manager(
                instance_config=cache_config,
                instance_id=f"{self.model.__name__}_{id(cache_config)}"
            )
    
    def _init_hooks(self, hook_config: Union[bool, HookConfig]):
        """初始化Hook系统"""
        if hook_config is False:
            self.hook_manager = None
        elif hook_config is True:
            self.hook_manager = HookManager(HookConfig())
        else:
            self.hook_manager = HookManager(hook_config)

        # 自动注册全局Hook
        if self.hook_manager:
            from ..features.hooks.registry import auto_register_hooks_to_crud
            auto_register_hooks_to_crud(self)

    def register_hook_class(self, hook_class):
        """
        注册Hook类到当前CRUD实例

        Args:
            hook_class: Hook类，继承自ModelHooks

        Example:
            user_crud.register_hook_class(UserHooks)
        """
        if hasattr(hook_class, 'register_to_crud'):
            hook_class.register_to_crud(self)
        else:
            raise ValueError(f"{hook_class} 必须继承自 ModelHooks")

    async def execute_hook(self, stage, data=None, **kwargs):
        """
        手动执行Hook

        Args:
            stage: Hook阶段
            data: 传递给Hook的数据
            **kwargs: 额外参数（包括依赖注入参数）

        Returns:
            处理后的数据

        Example:
            result = await user_crud.execute_hook(
                HookStage.PRE_CREATE,
                {"username": "test"},
                current_user=current_user,
                audit_service=audit_service
            )
        """
        if not self.hook_manager:
            return data

        from ..features.hooks.types import HookContext
        context = HookContext(
            stage=stage,
            model=self.model,
            data=data
        )

        # 将kwargs添加到context.extra中，供依赖注入使用
        context.extra.update(kwargs)

        return await self.hook_manager.execute_hooks(stage, data, context)

    def _init_monitoring(self, monitoring_config: Union[bool, MonitoringConfig]):
        """初始化监控"""
        if monitoring_config is False:
            self.monitoring_manager = None
        elif monitoring_config is True:
            self.monitoring_manager = MonitoringManager(MonitoringConfig())
        else:
            self.monitoring_manager = MonitoringManager(monitoring_config)
    
    def _create_router(self) -> APIRouter:
        """创建API路由"""
        self.factory = CrudRouteFactory(
            model=self.model,
            config=self.config,
            cache_manager=self.cache_manager,
            hook_manager=self.hook_manager,
            monitoring_manager=self.monitoring_manager
        )
        return self.factory.create_router()

    @property
    def crud_routes(self):
        """获取CRUD路由实例"""
        if hasattr(self, 'factory'):
            return self.factory.crud_routes
        return None
    
    @property
    def router(self) -> APIRouter:
        """获取API路由器"""
        return self._router
    
    def hook(self, stage: Union[str, "HookStage"], priority: Union[str, "HookPriority"] = "normal", name: str = None):
        """
        Hook装饰器 - 支持依赖注入

        Args:
            stage: Hook阶段
            priority: 优先级
            name: Hook名称

        Returns:
            装饰器函数

        Example:
            @crud.hook(HookStage.PRE_CREATE)
            async def pre_create_hook(
                data: dict,
                context: HookContext,
                current_user: dict = Depends(get_current_user)
            ) -> dict:
                return data
        """
        if not self.hook_manager:
            raise ValueError("Hook system is not enabled")

        def decorator(func):
            self.hook_manager.register(
                stage=stage,
                func=func,
                priority=priority,
                name=name or f"{self.model.__name__}.{func.__name__}"
            )
            return func
        return decorator
    
    def add_custom_route(self, path: str, methods: List[str] = None, **kwargs):
        """添加自定义路由"""
        methods = methods or ["GET"]
        
        def decorator(func):
            for method in methods:
                self._router.add_api_route(
                    path, func, methods=[method], **kwargs
                )
            return func
        return decorator
    
    # 便捷方法
    def get(self, path: str, **kwargs):
        """GET路由装饰器"""
        return self.add_custom_route(path, ["GET"], **kwargs)
    
    def post(self, path: str, **kwargs):
        """POST路由装饰器"""
        return self.add_custom_route(path, ["POST"], **kwargs)
    
    def put(self, path: str, **kwargs):
        """PUT路由装饰器"""
        return self.add_custom_route(path, ["PUT"], **kwargs)
    
    def delete(self, path: str, **kwargs):
        """DELETE路由装饰器"""
        return self.add_custom_route(path, ["DELETE"], **kwargs)
    
    # 配置方法
    def enable_cache(self, config: CacheConfig = None):
        """启用缓存"""
        self._init_cache(config or CacheConfig())
        self._router = self._create_router()
    
    def enable_hooks(self, config: HookConfig = None):
        """启用Hook系统"""
        self._init_hooks(config or HookConfig())
        self._router = self._create_router()
    
    def enable_monitoring(self, config: MonitoringConfig = None):
        """启用监控"""
        self._init_monitoring(config or MonitoringConfig())
        self._router = self._create_router()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "model": self.model.__name__,
            "cache_enabled": self.cache_manager is not None,
            "hooks_enabled": self.hook_manager is not None,
            "monitoring_enabled": self.monitoring_manager is not None,
        }
        
        if self.monitoring_manager:
            stats.update(self.monitoring_manager.get_stats())
        
        return stats


__all__ = ["FastCRUD"]
