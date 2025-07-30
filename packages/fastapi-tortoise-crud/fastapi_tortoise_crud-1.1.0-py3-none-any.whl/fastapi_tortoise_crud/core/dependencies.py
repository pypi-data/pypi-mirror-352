"""
依赖注入配置

支持精细化的依赖控制和Hook依赖注入
"""

import asyncio
import inspect
from typing import Dict, List, Any, Callable, Optional, Union, get_type_hints
from fastapi import Depends
from dataclasses import dataclass, field
from enum import Enum


class EndpointType(str, Enum):
    """端点类型枚举"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    BULK_CREATE = "bulk_create"
    BULK_DELETE = "bulk_delete"
    ALL = "all"  # 应用到所有端点


@dataclass
class DependencyConfig:
    """
    依赖配置类
    
    支持精细化的依赖控制
    """
    
    # 全局依赖（应用到所有端点）
    global_dependencies: List[Depends] = field(default_factory=list)
    
    # 端点特定依赖
    endpoint_dependencies: Dict[EndpointType, List[Depends]] = field(default_factory=dict)
    
    # 排除特定端点的全局依赖
    exclude_global: List[EndpointType] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保endpoint_dependencies包含所有端点类型
        for endpoint_type in EndpointType:
            if endpoint_type not in self.endpoint_dependencies:
                self.endpoint_dependencies[endpoint_type] = []
    
    def get_dependencies_for_endpoint(self, endpoint_type: EndpointType) -> List[Depends]:
        """
        获取指定端点的依赖列表
        
        Args:
            endpoint_type: 端点类型
            
        Returns:
            List[Depends]: 依赖列表
        """
        dependencies = []
        
        # 添加全局依赖（如果未被排除）
        if endpoint_type not in self.exclude_global:
            dependencies.extend(self.global_dependencies)
        
        # 添加端点特定依赖
        dependencies.extend(self.endpoint_dependencies.get(endpoint_type, []))
        
        return dependencies
    
    def add_global_dependency(self, dependency: Depends):
        """添加全局依赖"""
        self.global_dependencies.append(dependency)
    
    def add_endpoint_dependency(self, endpoint_type: EndpointType, dependency: Depends):
        """添加端点特定依赖"""
        if endpoint_type not in self.endpoint_dependencies:
            self.endpoint_dependencies[endpoint_type] = []
        self.endpoint_dependencies[endpoint_type].append(dependency)
    
    def exclude_global_for_endpoint(self, endpoint_type: EndpointType):
        """排除特定端点的全局依赖"""
        if endpoint_type not in self.exclude_global:
            self.exclude_global.append(endpoint_type)
    
    def remove_global_dependency(self, dependency: Depends):
        """移除全局依赖"""
        if dependency in self.global_dependencies:
            self.global_dependencies.remove(dependency)
    
    def remove_endpoint_dependency(self, endpoint_type: EndpointType, dependency: Depends):
        """移除端点特定依赖"""
        if endpoint_type in self.endpoint_dependencies:
            if dependency in self.endpoint_dependencies[endpoint_type]:
                self.endpoint_dependencies[endpoint_type].remove(dependency)





class DependencyResolver:
    """
    依赖解析器

    负责解析和注入依赖
    """

    def __init__(self):
        self._fastapi_style_hooks: Dict[str, Callable] = {}

    def register_fastapi_style_hook(self, hook_name: str, hook_func: Callable):
        """
        注册FastAPI风格的Hook

        Args:
            hook_name: Hook名称
            hook_func: Hook函数（参数中包含Depends()）
        """
        self._fastapi_style_hooks[hook_name] = hook_func

    async def resolve_hook_dependencies(
        self,
        hook_name: str,
        context: Any = None
    ) -> Dict[str, Any]:
        """
        解析Hook依赖

        Args:
            hook_name: Hook名称
            context: Hook上下文

        Returns:
            Dict[str, Any]: 解析后的依赖字典
        """
        resolved = {}

        # 解析FastAPI风格的依赖
        if hook_name in self._fastapi_style_hooks:
            hook_func = self._fastapi_style_hooks[hook_name]
            fastapi_resolved = await self._resolve_fastapi_style_dependencies(hook_func, context)
            resolved.update(fastapi_resolved)

        return resolved

    async def _resolve_fastapi_style_dependencies(self, hook_func: Callable, context: Any = None) -> Dict[str, Any]:
        """
        解析FastAPI风格的依赖

        Args:
            hook_func: Hook函数
            context: Hook上下文

        Returns:
            Dict[str, Any]: 解析后的依赖字典
        """
        resolved = {}

        # 获取函数签名
        sig = inspect.signature(hook_func)

        for param_name, param in sig.parameters.items():
            # 跳过标准的Hook参数
            if param_name in ['self', 'data', 'context']:
                continue

            # 检查是否有默认值且是Depends实例
            if (param.default != inspect.Parameter.empty and
                hasattr(param.default, '__class__') and
                param.default.__class__.__name__ == 'Depends'):
                dependency_func = param.default.dependency
                try:
                    # 解析依赖
                    if context and hasattr(context, 'request'):
                        value = await self._resolve_from_request(dependency_func, context.request)
                    else:
                        # 尝试从上下文的额外参数中获取
                        if context and hasattr(context, 'extra') and param_name in context.extra:
                            value = context.extra[param_name]
                        else:
                            if asyncio.iscoroutinefunction(dependency_func):
                                value = await dependency_func()
                            else:
                                value = dependency_func()

                    resolved[param_name] = value

                except Exception as e:
                    # 如果解析失败，尝试从上下文获取
                    if context and hasattr(context, 'extra') and param_name in context.extra:
                        resolved[param_name] = context.extra[param_name]
                    else:
                        # 记录警告但不抛出异常，让Hook继续执行
                        import logging
                        logging.warning(f"无法解析Hook依赖 {param_name}: {e}")
                        resolved[param_name] = None

        return resolved

    async def _resolve_from_request(self, dependency: Callable, request: Any) -> Any:
        """从请求中解析依赖"""
        import inspect
        import asyncio
        from fastapi import Header
        from fastapi.dependencies.utils import get_dependant, solve_dependencies

        try:
            # 使用FastAPI的依赖解析系统
            dependant = get_dependant(path="", call=dependency)

            # 解析依赖
            values, errors, _, _, _ = await solve_dependencies(
                request=request,
                dependant=dependant,
                body=None,
                dependency_overrides_provider=None
            )

            if errors:
                # 如果有错误，尝试手动解析
                return await self._manual_resolve_dependency(dependency, request)

            # 如果依赖函数没有参数，直接返回调用结果
            if not dependant.dependencies:
                if asyncio.iscoroutinefunction(dependency):
                    return await dependency()
                else:
                    return dependency()

            # 调用依赖函数并传递解析的参数
            if asyncio.iscoroutinefunction(dependency):
                return await dependency(**values)
            else:
                return dependency(**values)

        except Exception as e:
            # 如果FastAPI解析失败，尝试手动解析
            return await self._manual_resolve_dependency(dependency, request)

    async def _manual_resolve_dependency(self, dependency: Callable, request: Any) -> Any:
        """手动解析依赖（备用方案）"""
        import inspect
        import asyncio

        # 获取依赖函数的签名
        sig = inspect.signature(dependency)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'request':
                kwargs[param_name] = request
            elif hasattr(param.default, '__class__') and param.default.__class__.__name__ == 'Header':
                # 处理Header参数
                header_name = param.default.alias or param_name.replace('_', '-')
                header_value = request.headers.get(header_name) if hasattr(request, 'headers') else None
                kwargs[param_name] = header_value

        # 调用依赖函数
        if asyncio.iscoroutinefunction(dependency):
            return await dependency(**kwargs)
        else:
            return dependency(**kwargs)
    
    def clear_hook_dependencies(self, hook_name: str = None):
        """清空Hook依赖"""
        if hook_name:
            self._fastapi_style_hooks.pop(hook_name, None)
        else:
            self._fastapi_style_hooks.clear()


# 全局依赖解析器实例
_global_dependency_resolver = DependencyResolver()


def get_dependency_resolver() -> DependencyResolver:
    """获取全局依赖解析器"""
    return _global_dependency_resolver





__all__ = [
    "EndpointType",
    "DependencyConfig",
    "DependencyResolver",
    "get_dependency_resolver"
]

"""
使用示例：

# 1. 精细化依赖控制
from fastapi import Depends

def get_current_user():
    return {"id": 1, "username": "admin"}

def get_admin_user():
    return {"id": 1, "username": "admin", "is_admin": True}

# 创建依赖配置
deps = DependencyConfig(
    global_dependencies=[Depends(get_current_user)],  # 所有端点都需要用户认证
    endpoint_dependencies={
        EndpointType.CREATE: [Depends(get_admin_user)],  # 创建需要管理员权限
        EndpointType.DELETE: [Depends(get_admin_user)],  # 删除需要管理员权限
    },
    exclude_global=[EndpointType.READ]  # 读取端点不需要认证
)

user_crud = FastCRUD(User, dependencies=deps)

# 2. Hook依赖注入
@hook_dependency(get_current_user, "user")
@user_crud.hook("pre_create")
async def validate_permission(data, context, user):
    if not user.get("is_admin"):
        raise PermissionError("需要管理员权限")
    return data
"""
