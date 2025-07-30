"""
Hook系统类型定义
"""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


class HookStage(str, Enum):
    """Hook执行阶段"""
    
    # 验证阶段
    PRE_VALIDATE = "pre_validate"
    POST_VALIDATE = "post_validate"
    
    # CRUD操作阶段
    PRE_CREATE = "pre_create"
    POST_CREATE = "post_create"
    PRE_READ = "pre_read"
    POST_READ = "post_read"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"
    PRE_DELETE = "pre_delete"
    POST_DELETE = "post_delete"
    PRE_LIST = "pre_list"
    POST_LIST = "post_list"
    
    # 缓存阶段
    ON_CACHE_HIT = "on_cache_hit"
    ON_CACHE_MISS = "on_cache_miss"
    ON_CACHE_SET = "on_cache_set"
    ON_CACHE_DELETE = "on_cache_delete"
    
    # 错误处理阶段
    ON_ERROR = "on_error"
    ON_VALIDATION_ERROR = "on_validation_error"
    
    # 自定义阶段
    CUSTOM = "custom"


class HookPriority(str, Enum):
    """Hook优先级"""
    
    HIGHEST = "highest"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    LOWEST = "lowest"


@dataclass
class HookContext:
    """Hook执行上下文"""
    
    # 基础信息
    stage: HookStage
    model: Optional[Any] = None
    request: Optional[Any] = None
    
    # 操作数据
    data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    
    # 标识信息
    id: Optional[Any] = None
    ids: Optional[list] = None
    
    # 扩展数据
    extra: Dict[str, Any] = field(default_factory=dict)
    
    # 错误信息
    error: Optional[Exception] = None

    # 新增：支持修改request和response
    request_modifications: Dict[str, Any] = field(default_factory=dict)
    response_modifications: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.extra.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置上下文数据"""
        self.extra[key] = value
    
    def update(self, **kwargs):
        """批量更新上下文数据"""
        self.extra.update(kwargs)

    def modify_request_header(self, key: str, value: str):
        """修改请求头"""
        if "headers" not in self.request_modifications:
            self.request_modifications["headers"] = {}
        self.request_modifications["headers"][key] = value

    def modify_request_body(self, new_body: Dict[str, Any]):
        """修改请求体"""
        self.request_modifications["body"] = new_body

    def modify_response_header(self, key: str, value: str):
        """修改响应头"""
        if "headers" not in self.response_modifications:
            self.response_modifications["headers"] = {}
        self.response_modifications["headers"][key] = value

    def modify_response_data(self, new_data: Dict[str, Any]):
        """修改响应数据"""
        self.response_modifications["data"] = new_data

    def add_response_cookie(self, key: str, value: str, **kwargs):
        """添加响应Cookie"""
        if "cookies" not in self.response_modifications:
            self.response_modifications["cookies"] = {}
        self.response_modifications["cookies"][key] = {"value": value, **kwargs}
    
    def copy(self) -> "HookContext":
        """复制上下文"""
        return HookContext(
            stage=self.stage,
            model=self.model,
            request=self.request,
            data=self.data.copy() if self.data else None,
            original_data=self.original_data.copy() if self.original_data else None,
            id=self.id,
            ids=self.ids.copy() if self.ids else None,
            extra=self.extra.copy(),
            error=self.error,
            request_modifications=self.request_modifications.copy(),
            response_modifications=self.response_modifications.copy()
        )


@dataclass
class HookInfo:
    """Hook信息"""
    
    name: str
    stage: HookStage
    priority: HookPriority
    function: Any
    enabled: bool = True
    description: str = ""
    
    # 执行条件
    condition: Optional[Any] = None
    
    # 统计信息
    call_count: int = 0
    error_count: int = 0
    total_time: float = 0.0
    
    def __post_init__(self):
        if not self.name:
            self.name = getattr(self.function, '__name__', 'unknown')
        if not self.description:
            self.description = getattr(self.function, '__doc__', '') or f"Hook for {self.stage}"


__all__ = [
    "HookStage",
    "HookPriority",
    "HookContext", 
    "HookInfo"
]
