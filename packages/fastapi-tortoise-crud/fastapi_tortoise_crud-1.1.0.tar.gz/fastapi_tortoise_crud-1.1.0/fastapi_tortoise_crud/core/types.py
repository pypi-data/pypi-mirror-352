"""
核心类型定义
"""

from typing import Type, List, Optional, Any, Dict, Union
from dataclasses import dataclass, field
from fastapi import Depends
from pydantic import BaseModel as PydanticModel
from tortoise.models import Model


@dataclass
class CrudConfig:
    """CRUD配置类"""
    
    # 路由配置
    prefix: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Schema配置
    create_schema: Optional[Type[PydanticModel]] = None
    read_schema: Optional[Type[PydanticModel]] = None
    update_schema: Optional[Type[PydanticModel]] = None
    
    # 关系配置
    relations: List[str] = field(default_factory=list)
    preload_relations: List[str] = field(default_factory=list)
    
    # 依赖注入
    dependencies: Union[List[Depends], "DependencyConfig"] = field(default_factory=list)
    
    # 分页配置
    default_page_size: int = 20
    max_page_size: int = 100
    
    # 其他配置
    enable_soft_delete: bool = False
    enable_timestamps: bool = True

    # 查询配置
    text_contains_search: bool = True  # 文本字段是否使用包含查询

    # 调试配置
    debug_mode: bool = False  # 调试模式，控制详细日志输出

    # 自定义配置
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteConfig:
    """路由配置类"""
    
    # 启用的路由
    enable_list: bool = True
    enable_create: bool = True
    enable_read: bool = True
    enable_update: bool = True
    enable_delete: bool = True
    enable_bulk_create: bool = True
    enable_bulk_delete: bool = True
    
    # 路由路径自定义
    list_path: str = "/list"
    create_path: str = "/create"
    read_path: str = "/read"
    update_path: str = "/update"
    delete_path: str = "/delete"
    bulk_create_path: str = "/bulk-create"
    bulk_delete_path: str = "/bulk-delete"
    
    # 路由方法自定义
    list_methods: List[str] = field(default_factory=lambda: ["POST"])
    create_methods: List[str] = field(default_factory=lambda: ["POST"])
    read_methods: List[str] = field(default_factory=lambda: ["GET"])
    update_methods: List[str] = field(default_factory=lambda: ["PUT"])
    delete_methods: List[str] = field(default_factory=lambda: ["DELETE"])


# ValidationConfig 已移除，验证功能由 Pydantic 提供


__all__ = [
    "CrudConfig",
    "RouteConfig"
]
