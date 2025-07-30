"""
Hook管理器

管理Hook的注册、执行和生命周期
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable, Union
from collections import defaultdict

from .config import HookConfig
from .types import HookStage, HookPriority, HookContext, HookInfo

logger = logging.getLogger(__name__)


class HookManager:
    """
    Hook管理器
    
    负责Hook的注册、执行和管理
    """
    
    def __init__(self, config: HookConfig = None):
        """
        初始化Hook管理器
        
        Args:
            config: Hook配置
        """
        self.config = config or HookConfig()
        self._hooks: Dict[HookStage, List[HookInfo]] = defaultdict(list)
        self._enabled = self.config.enabled
        
        # 设置日志级别
        if self.config.debug_mode:
            logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))
    
    @property
    def enabled(self) -> bool:
        """Hook系统是否启用"""
        return self._enabled
    
    def register(
        self,
        stage: Union[str, HookStage],
        func: Callable,
        priority: Union[str, HookPriority] = HookPriority.NORMAL,
        name: str = None,
        description: str = None,
        condition: Callable = None,
        enabled: bool = True
    ) -> HookInfo:
        """
        注册Hook
        
        Args:
            stage: Hook阶段
            func: Hook函数
            priority: 优先级
            name: Hook名称
            description: Hook描述
            condition: 执行条件函数
            enabled: 是否启用
            
        Returns:
            HookInfo: Hook信息对象
        """
        if isinstance(stage, str):
            stage = HookStage(stage)
        if isinstance(priority, str):
            priority = HookPriority(priority)
        
        hook_info = HookInfo(
            name=name or getattr(func, '__name__', 'unknown'),
            stage=stage,
            priority=priority,
            function=func,
            enabled=enabled,
            description=description or getattr(func, '__doc__', ''),
            condition=condition
        )

        # 检查是否是FastAPI风格的Hook（参数中包含Depends）
        self._register_fastapi_style_hook_if_needed(hook_info)
        
        # 按优先级插入
        hooks_for_stage = self._hooks[stage]
        priority_weight = self.config.get_priority_weight(priority)
        
        inserted = False
        for i, existing_hook in enumerate(hooks_for_stage):
            existing_weight = self.config.get_priority_weight(existing_hook.priority)
            if priority_weight > existing_weight:
                hooks_for_stage.insert(i, hook_info)
                inserted = True
                break
        
        if not inserted:
            hooks_for_stage.append(hook_info)
        
        if self.config.debug_mode:
            logger.debug(f"注册Hook: {hook_info.name} ({stage}, {priority})")
        
        return hook_info
    
    def unregister(self, stage: Union[str, HookStage], name: str) -> bool:
        """
        注销Hook
        
        Args:
            stage: Hook阶段
            name: Hook名称
            
        Returns:
            bool: 是否成功注销
        """
        if isinstance(stage, str):
            stage = HookStage(stage)
        
        hooks_for_stage = self._hooks[stage]
        for i, hook_info in enumerate(hooks_for_stage):
            if hook_info.name == name:
                hooks_for_stage.pop(i)
                if self.config.debug_mode:
                    logger.debug(f"注销Hook: {name} ({stage})")
                return True
        
        return False
    
    def get_hooks(self, stage: Union[str, HookStage]) -> List[HookInfo]:
        """
        获取指定阶段的Hook列表
        
        Args:
            stage: Hook阶段
            
        Returns:
            List[HookInfo]: Hook信息列表
        """
        if isinstance(stage, str):
            stage = HookStage(stage)
        
        return [hook for hook in self._hooks[stage] if hook.enabled]
    
    async def execute_hooks(
        self,
        stage: Union[str, HookStage],
        data: Any = None,
        context: HookContext = None,
        **kwargs
    ) -> Any:
        """
        执行指定阶段的所有Hook
        
        Args:
            stage: Hook阶段
            data: 传递给Hook的数据
            context: Hook执行上下文
            **kwargs: 额外参数
            
        Returns:
            Any: 处理后的数据
        """
        if not self._enabled:
            return data
        
        if isinstance(stage, str):
            stage = HookStage(stage)
        
        hooks = self.get_hooks(stage)
        if not hooks:
            return data
        
        # 创建或更新上下文
        if context is None:
            context = HookContext(stage=stage, data=data, **kwargs)
        else:
            context.stage = stage
            if data is not None:
                context.data = data
            context.update(**kwargs)
        
        if self.config.debug_mode:
            logger.debug(f"执行{len(hooks)}个Hook: {stage}")
        
        start_time = time.time()
        
        try:
            # 应用全局过滤器
            for filter_func in self.config.global_filters:
                if not filter_func(context):
                    if self.config.debug_mode:
                        logger.debug(f"Hook被全局过滤器拦截: {stage}")
                    return data
            
            # 执行Hook
            current_data = data
            for hook_info in hooks:
                try:
                    # 检查执行条件
                    if hook_info.condition and not hook_info.condition(context):
                        continue
                    
                    # 执行Hook
                    hook_start_time = time.time()

                    # 解析Hook依赖
                    hook_kwargs = await self._resolve_hook_dependencies(hook_info.name, context)

                    if asyncio.iscoroutinefunction(hook_info.function):
                        result = await asyncio.wait_for(
                            hook_info.function(current_data, context, **hook_kwargs),
                            timeout=self.config.timeout_per_hook
                        )
                    else:
                        result = hook_info.function(current_data, context, **hook_kwargs)
                    
                    # 更新数据
                    if result is not None:
                        current_data = result
                        context.data = current_data
                    
                    # 更新统计信息
                    if self.config.enable_timing:
                        hook_info.total_time += time.time() - hook_start_time
                    hook_info.call_count += 1
                    
                    if self.config.debug_mode:
                        logger.debug(f"Hook执行成功: {hook_info.name}")
                
                except asyncio.TimeoutError:
                    hook_info.error_count += 1
                    error_msg = f"Hook超时: {hook_info.name} (>{self.config.timeout_per_hook}s)"
                    logger.error(error_msg)
                    
                    if self.config.stop_on_error:
                        raise TimeoutError(error_msg)
                
                except Exception as e:
                    hook_info.error_count += 1
                    error_msg = f"Hook执行失败: {hook_info.name} - {e}"

                    if self.config.log_errors:
                        logger.error(error_msg, exc_info=True)

                    # 执行错误处理Hook
                    context.error = e
                    try:
                        await self.execute_hooks(HookStage.ON_ERROR, current_data, context)
                    except Exception as error_hook_exception:
                        logger.error(f"错误处理Hook也失败了: {error_hook_exception}")

                    # Hook异常应该中断整个请求的后续执行
                    if self.config.stop_on_error:
                        raise e
                    else:
                        # Hook异常应该中断整个请求，不只是Hook内部
                        logger.error(f"Hook异常，中断整个请求: {stage} - {e}")
                        raise e
                
                # 检查总执行时间
                if time.time() - start_time > self.config.max_execution_time:
                    logger.warning(f"Hook执行超时: {stage} (>{self.config.max_execution_time}s)")
                    break
            
            return current_data
        
        except Exception as e:
            if self.config.log_errors:
                logger.error(f"Hook执行阶段失败: {stage} - {e}", exc_info=True)

            # Hook异常应该总是中断整个请求，不管stop_on_error设置如何
            # 因为Hook异常通常表示业务逻辑错误（如权限不足、验证失败等）
            raise e
    
    def enable_hook(self, stage: Union[str, HookStage], name: str) -> bool:
        """启用Hook"""
        if isinstance(stage, str):
            stage = HookStage(stage)
        
        for hook_info in self._hooks[stage]:
            if hook_info.name == name:
                hook_info.enabled = True
                return True
        return False
    
    def disable_hook(self, stage: Union[str, HookStage], name: str) -> bool:
        """禁用Hook"""
        if isinstance(stage, str):
            stage = HookStage(stage)
        
        for hook_info in self._hooks[stage]:
            if hook_info.name == name:
                hook_info.enabled = False
                return True
        return False
    
    def clear_hooks(self, stage: Union[str, HookStage] = None):
        """清空Hook"""
        if stage is None:
            self._hooks.clear()
        else:
            if isinstance(stage, str):
                stage = HookStage(stage)
            self._hooks[stage].clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Hook统计信息"""
        stats = {
            "enabled": self._enabled,
            "total_hooks": sum(len(hooks) for hooks in self._hooks.values()),
            "stages": {}
        }
        
        for stage, hooks in self._hooks.items():
            stage_stats = {
                "total": len(hooks),
                "enabled": len([h for h in hooks if h.enabled]),
                "hooks": []
            }
            
            for hook_info in hooks:
                hook_stats = {
                    "name": hook_info.name,
                    "priority": hook_info.priority,
                    "enabled": hook_info.enabled,
                    "call_count": hook_info.call_count,
                    "error_count": hook_info.error_count
                }
                
                if self.config.enable_timing:
                    hook_stats["total_time"] = hook_info.total_time
                    hook_stats["avg_time"] = (
                        hook_info.total_time / hook_info.call_count
                        if hook_info.call_count > 0 else 0
                    )
                
                stage_stats["hooks"].append(hook_stats)
            
            stats["stages"][stage.value] = stage_stats
        
        return stats

    def reset_stats(self):
        """重置统计信息"""
        for hooks in self._hooks.values():
            for hook_info in hooks:
                hook_info.call_count = 0
                hook_info.error_count = 0
                hook_info.total_time = 0.0

    def _register_fastapi_style_hook_if_needed(self, hook_info):
        """
        检查并注册FastAPI风格的Hook

        Args:
            hook_info: Hook信息对象
        """
        import inspect
        from fastapi import Depends

        # 获取函数签名
        sig = inspect.signature(hook_info.function)

        # 检查是否有参数使用了Depends
        has_depends = False
        for param_name, param in sig.parameters.items():
            if param_name in ['data', 'context']:
                continue
            if (param.default != inspect.Parameter.empty and
                hasattr(param.default, '__class__') and
                param.default.__class__.__name__ == 'Depends'):
                has_depends = True
                break

        # 如果有Depends参数，注册到依赖解析器
        if has_depends:
            try:
                from ...core.dependencies import get_dependency_resolver
                resolver = get_dependency_resolver()
                resolver.register_fastapi_style_hook(hook_info.name, hook_info.function)
            except ImportError:
                # 如果依赖模块不可用，忽略
                pass

    async def _resolve_hook_dependencies(self, hook_name: str, context: Any = None) -> Dict[str, Any]:
        """
        解析Hook依赖

        Args:
            hook_name: Hook名称
            context: Hook上下文

        Returns:
            Dict[str, Any]: 解析后的依赖字典
        """
        try:
            from ...core.dependencies import get_dependency_resolver
            resolver = get_dependency_resolver()
            return await resolver.resolve_hook_dependencies(hook_name, context)
        except ImportError:
            # 如果依赖模块不可用，返回空字典
            return {}
        except Exception as e:
            if self.config.log_errors:
                logger.warning(f"Hook依赖解析失败 {hook_name}: {e}")
            return {}


__all__ = ["HookManager"]
