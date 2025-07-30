"""
全局Hook注册表

管理全局注册的Hook函数
"""

from typing import Dict, List, Callable, Type, Any
from collections import defaultdict
from .types import HookStage

# 全局Hook注册表
_global_hooks: Dict[Type, Dict[HookStage, List[Callable]]] = defaultdict(lambda: defaultdict(list))
_all_hooks: List[Callable] = []


def register_global_hook(func: Callable):
    """
    注册全局Hook
    
    Args:
        func: Hook函数
    """
    if not hasattr(func, '_hook_info'):
        return
    
    hook_info = func._hook_info
    model = hook_info.get('model')
    stage = hook_info.get('stage')
    
    if isinstance(stage, str):
        stage = HookStage(stage)
    
    # 添加到全局列表
    if func not in _all_hooks:
        _all_hooks.append(func)
    
    # 如果指定了模型，添加到模型特定的Hook列表
    if model:
        if func not in _global_hooks[model][stage]:
            _global_hooks[model][stage].append(func)


def get_hooks_for_model(model: Type, stage: HookStage) -> List[Callable]:
    """
    获取指定模型和阶段的Hook列表
    
    Args:
        model: 模型类
        stage: Hook阶段
        
    Returns:
        List[Callable]: Hook函数列表
    """
    return _global_hooks.get(model, {}).get(stage, [])


def get_all_hooks() -> List[Callable]:
    """
    获取所有注册的Hook

    Returns:
        List[Callable]: 所有Hook函数列表
    """
    return _all_hooks.copy()


def get_global_hooks() -> Dict[Type, Dict[HookStage, List[Callable]]]:
    """
    获取全局Hook注册表

    Returns:
        Dict: 全局Hook注册表
    """
    return dict(_global_hooks)


def clear_global_hooks():
    """清除所有全局Hook"""
    _global_hooks.clear()
    _all_hooks.clear()


def clear_hooks(model: Type = None):
    """
    清除Hook
    
    Args:
        model: 模型类，如果为None则清除所有Hook
    """
    if model:
        if model in _global_hooks:
            del _global_hooks[model]
    else:
        _global_hooks.clear()
        _all_hooks.clear()


def auto_register_hooks_to_crud(crud_instance):
    """
    自动将全局Hook注册到CRUD实例
    
    Args:
        crud_instance: FastCRUD实例
    """
    if not hasattr(crud_instance, 'hook_manager') or not crud_instance.hook_manager:
        return
    
    model = crud_instance.model
    
    # 注册模型特定的Hook
    for stage, hooks in _global_hooks.get(model, {}).items():
        for hook_func in hooks:
            hook_info = hook_func._hook_info
            crud_instance.hook_manager.register(
                stage=stage,
                func=hook_func,
                priority=hook_info.get('priority'),
                name=hook_info.get('name'),
                description=hook_info.get('description'),
                condition=hook_info.get('condition'),
                enabled=hook_info.get('enabled', True)
            )
    
    # 注册通用Hook（没有指定模型的）
    for hook_func in _all_hooks:
        hook_info = hook_func._hook_info
        if not hook_info.get('model'):  # 没有指定模型的Hook
            crud_instance.hook_manager.register(
                stage=hook_info.get('stage'),
                func=hook_func,
                priority=hook_info.get('priority'),
                name=hook_info.get('name'),
                description=hook_info.get('description'),
                condition=hook_info.get('condition'),
                enabled=hook_info.get('enabled', True)
            )


__all__ = [
    "register_global_hook",
    "get_hooks_for_model",
    "get_all_hooks",
    "get_global_hooks",
    "clear_global_hooks",
    "clear_hooks",
    "auto_register_hooks_to_crud"
]
