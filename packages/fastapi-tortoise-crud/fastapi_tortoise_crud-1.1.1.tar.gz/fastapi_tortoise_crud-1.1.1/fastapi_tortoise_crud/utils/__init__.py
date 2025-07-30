"""
工具模块

提供异常处理、验证器等工具功能
"""

from .exceptions import (
    CrudException,
    ValidationError,
    NotFoundError,
    DuplicateError,
    PermissionError,
    setup_exception_handlers
)
# 验证功能由 Pydantic 提供，移除自定义验证器
from .helpers import generate_cache_key, format_error_message

__all__ = [
    # 异常类
    "CrudException",
    "ValidationError", 
    "NotFoundError",
    "DuplicateError",
    "PermissionError",
    "setup_exception_handlers",
    
    # 验证功能由 Pydantic 提供
    
    # 辅助函数
    "generate_cache_key",
    "format_error_message"
]
