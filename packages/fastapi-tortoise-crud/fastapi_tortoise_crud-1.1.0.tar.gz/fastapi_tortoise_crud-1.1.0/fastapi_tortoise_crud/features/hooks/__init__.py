"""
Hook系统

提供两种Hook机制：
1. 基于类的Hook - 面向对象，支持依赖注入
2. 装饰器Hook - 简洁优雅，支持依赖注入（通过FastCRUD实例的hook方法）
"""

from .types import HookStage, HookPriority, HookContext, HookInfo
from .config import HookConfig
from .manager import HookManager
from .registry import get_global_hooks, get_hooks_for_model, clear_global_hooks
from .response_handler import ResponseHandler

# 基于类的Hook系统
from .class_based import (
    ModelHooks, register_model_hooks,
    get_registered_hook_classes
)

__all__ = [
    # 核心类型
    "HookStage",
    "HookPriority",
    "HookContext",
    "HookInfo",

    # 配置和管理
    "HookConfig",
    "HookManager",

    # 注册表
    "get_global_hooks",
    "get_hooks_for_model",
    "clear_global_hooks",

    # 基于类的Hook
    "ModelHooks",
    "register_model_hooks",
    "get_registered_hook_classes",

    # 响应处理
    "ResponseHandler"
]
