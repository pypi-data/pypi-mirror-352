"""
Hook系统配置
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from .types import HookStage, HookPriority


@dataclass
class HookConfig:
    """Hook系统配置"""
    
    # 基础配置
    enabled: bool = True
    max_execution_time: float = 30.0  # 最大执行时间（秒）
    
    # 错误处理
    stop_on_error: bool = True  # 是否在错误时停止执行
    log_errors: bool = True  # 是否记录错误
    
    # 性能配置
    enable_timing: bool = True  # 是否启用执行时间统计
    enable_metrics: bool = True  # 是否启用指标收集
    
    # 并发配置
    max_concurrent_hooks: int = 10  # 最大并发Hook数量
    timeout_per_hook: float = 5.0  # 单个Hook超时时间
    
    # 调试配置
    debug_mode: bool = False  # 调试模式
    log_level: str = "INFO"  # 日志级别
    
    # 默认优先级映射
    priority_weights: Dict[HookPriority, int] = field(default_factory=lambda: {
        HookPriority.HIGHEST: 100,
        HookPriority.HIGH: 75,
        HookPriority.NORMAL: 50,
        HookPriority.LOW: 25,
        HookPriority.LOWEST: 10
    })
    
    # 阶段配置
    stage_config: Dict[HookStage, Dict[str, Any]] = field(default_factory=dict)
    
    # 全局Hook过滤器
    global_filters: List[Callable] = field(default_factory=list)
    
    def get_stage_config(self, stage: HookStage) -> Dict[str, Any]:
        """获取阶段特定配置"""
        return self.stage_config.get(stage, {})
    
    def set_stage_config(self, stage: HookStage, config: Dict[str, Any]):
        """设置阶段特定配置"""
        self.stage_config[stage] = config
    
    def get_priority_weight(self, priority: HookPriority) -> int:
        """获取优先级权重"""
        return self.priority_weights.get(priority, 50)
    
    def add_global_filter(self, filter_func: Callable):
        """添加全局过滤器"""
        self.global_filters.append(filter_func)
    
    def __post_init__(self):
        """配置验证"""
        if self.max_execution_time <= 0:
            raise ValueError("max_execution_time must be positive")
        
        if self.timeout_per_hook <= 0:
            raise ValueError("timeout_per_hook must be positive")
        
        if self.max_concurrent_hooks <= 0:
            raise ValueError("max_concurrent_hooks must be positive")


# 预定义配置
class HookPresets:
    """Hook预设配置"""
    
    @staticmethod
    def development() -> HookConfig:
        """开发环境配置"""
        return HookConfig(
            debug_mode=True,
            log_level="DEBUG",
            enable_timing=True,
            enable_metrics=True,
            stop_on_error=True
        )
    
    @staticmethod
    def production() -> HookConfig:
        """生产环境配置"""
        return HookConfig(
            debug_mode=False,
            log_level="WARNING",
            enable_timing=True,
            enable_metrics=True,
            stop_on_error=False,
            max_execution_time=10.0,
            timeout_per_hook=3.0
        )
    
    @staticmethod
    def performance() -> HookConfig:
        """性能优化配置"""
        return HookConfig(
            enable_timing=False,
            enable_metrics=False,
            log_errors=False,
            max_execution_time=5.0,
            timeout_per_hook=1.0,
            max_concurrent_hooks=20
        )
    
    @staticmethod
    def testing() -> HookConfig:
        """测试环境配置"""
        return HookConfig(
            debug_mode=True,
            log_level="DEBUG",
            stop_on_error=True,
            enable_timing=True,
            enable_metrics=True,
            max_execution_time=60.0  # 测试时允许更长时间
        )


__all__ = ["HookConfig", "HookPresets"]
