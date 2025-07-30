"""
基于类的Hook系统 - 更优雅的Hook定义方式
"""

from typing import Dict, Any, Optional, Type, List
from abc import ABC, abstractmethod
from .types import HookStage, HookContext, HookPriority
from .manager import HookManager


class ModelHooks(ABC):
    """
    模型Hook基类
    
    使用方式：
    class UserHooks(ModelHooks):
        model = User
        
        async def pre_create(self, data: dict, context: HookContext):
            # 处理逻辑
            return data
    """
    
    model: Type = None
    priority: HookPriority = HookPriority.NORMAL
    enabled: bool = True
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # 只有非基类才需要检查model属性
        if cls.__name__ != 'AutoModelHooks' and cls.model is None:
            raise ValueError(f"{cls.__name__} 必须指定 model 属性")
    
    # CRUD Hook方法
    async def pre_validate(self, data: dict, context: HookContext) -> dict:
        """验证前Hook"""
        return data
    
    async def post_validate(self, data: dict, context: HookContext) -> dict:
        """验证后Hook"""
        return data
    
    async def pre_create(self, data: dict, context: HookContext) -> dict:
        """创建前Hook"""
        return data
    
    async def post_create(self, data: dict, context: HookContext) -> dict:
        """创建后Hook"""
        return data
    
    async def pre_read(self, data: dict, context: HookContext) -> dict:
        """读取前Hook"""
        return data
    
    async def post_read(self, data: dict, context: HookContext) -> dict:
        """读取后Hook"""
        return data
    
    async def pre_update(self, data: dict, context: HookContext) -> dict:
        """更新前Hook"""
        return data
    
    async def post_update(self, data: dict, context: HookContext) -> dict:
        """更新后Hook"""
        return data
    
    async def pre_delete(self, data: dict, context: HookContext) -> dict:
        """删除前Hook"""
        return data
    
    async def post_delete(self, data: dict, context: HookContext) -> dict:
        """删除后Hook"""
        return data
    
    async def pre_list(self, data: dict, context: HookContext) -> dict:
        """列表查询前Hook"""
        return data
    
    async def post_list(self, data: dict, context: HookContext) -> dict:
        """列表查询后Hook"""
        return data
    
    # 缓存Hook方法
    async def on_cache_hit(self, data: dict, context: HookContext) -> dict:
        """缓存命中Hook"""
        return data
    
    async def on_cache_miss(self, data: dict, context: HookContext) -> dict:
        """缓存未命中Hook"""
        return data
    
    async def on_cache_set(self, data: dict, context: HookContext) -> dict:
        """缓存设置Hook"""
        return data
    
    async def on_cache_delete(self, data: dict, context: HookContext) -> dict:
        """缓存删除Hook"""
        return data
    
    # 错误处理Hook方法
    async def on_error(self, data: dict, context: HookContext) -> dict:
        """错误处理Hook"""
        return data
    
    async def on_validation_error(self, data: dict, context: HookContext) -> dict:
        """验证错误Hook"""
        return data
    
    @classmethod
    def register_to_manager(cls, hook_manager: HookManager):
        """将Hook类注册到管理器"""
        instance = cls()

        # 获取所有Hook方法
        hook_methods = {
            HookStage.PRE_VALIDATE: instance.pre_validate,
            HookStage.POST_VALIDATE: instance.post_validate,
            HookStage.PRE_CREATE: instance.pre_create,
            HookStage.POST_CREATE: instance.post_create,
            HookStage.PRE_READ: instance.pre_read,
            HookStage.POST_READ: instance.post_read,
            HookStage.PRE_UPDATE: instance.pre_update,
            HookStage.POST_UPDATE: instance.post_update,
            HookStage.PRE_DELETE: instance.pre_delete,
            HookStage.POST_DELETE: instance.post_delete,
            HookStage.PRE_LIST: instance.pre_list,
            HookStage.POST_LIST: instance.post_list,
            HookStage.ON_CACHE_HIT: instance.on_cache_hit,
            HookStage.ON_CACHE_MISS: instance.on_cache_miss,
            HookStage.ON_CACHE_SET: instance.on_cache_set,
            HookStage.ON_CACHE_DELETE: instance.on_cache_delete,
            HookStage.ON_ERROR: instance.on_error,
            HookStage.ON_VALIDATION_ERROR: instance.on_validation_error,
        }

        # 注册非默认实现的Hook
        for stage, method in hook_methods.items():
            # 检查是否重写了默认方法
            if cls._is_method_overridden(method, stage):
                hook_manager.register(
                    stage=stage,
                    func=method,
                    priority=cls.priority,
                    name=f"{cls.__name__}.{method.__name__}",
                    description=method.__doc__ or f"{cls.__name__} {stage} hook",
                    enabled=cls.enabled
                )

    @classmethod
    def register_to_crud(cls, crud_instance):
        """将Hook类注册到FastCRUD实例"""
        if hasattr(crud_instance, 'hook_manager') and crud_instance.hook_manager:
            cls.register_to_manager(crud_instance.hook_manager)
    
    @classmethod
    def _is_method_overridden(cls, method, stage: HookStage) -> bool:
        """检查方法是否被重写"""
        # 获取基类中对应的方法名
        method_name = stage.value
        base_method = getattr(ModelHooks, method_name, None)

        if base_method is None:
            return True  # 如果找不到基类方法，认为是重写的

        # 比较方法的代码对象
        try:
            return method.__func__ is not base_method.__func__
        except AttributeError:
            return True


def register_model_hooks(*hook_classes: Type[ModelHooks]):
    """
    注册多个模型Hook类的装饰器
    
    使用方式：
    @register_model_hooks(UserHooks, ProductHooks)
    def setup_hooks(hook_manager: HookManager):
        pass
    """
    def decorator(func):
        def wrapper(hook_manager: HookManager):
            for hook_class in hook_classes:
                hook_class.register_to_manager(hook_manager)
            return func(hook_manager) if func else None
        return wrapper
    return decorator


# 全局Hook类注册表
_registered_hook_classes: List[Type[ModelHooks]] = []


def auto_register_hook_class(hook_class: Type[ModelHooks]):
    """自动注册Hook类"""
    if hook_class not in _registered_hook_classes:
        _registered_hook_classes.append(hook_class)


def get_registered_hook_classes() -> List[Type[ModelHooks]]:
    """获取所有已注册的Hook类"""
    return _registered_hook_classes.copy()


class HookClassMeta(type):
    """Hook类元类，自动注册Hook类"""

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)

        # 如果是ModelHooks的子类且不是ModelHooks本身，自动注册
        if (bases and any(issubclass(base, ModelHooks) for base in bases)
            and name != 'ModelHooks' and name != 'AutoModelHooks'):
            auto_register_hook_class(cls)

        return cls


class AutoModelHooks(ModelHooks):
    """自动注册的模型Hook基类"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # 自动注册子类
        auto_register_hook_class(cls)
