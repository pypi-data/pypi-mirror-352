"""
向后兼容模块

保持与旧版本API的兼容性
"""

from .legacy import ModelCrud, BaseApiOut, init_cache, get_cache_manager

__all__ = [
    "ModelCrud",
    "BaseApiOut", 
    "init_cache",
    "get_cache_manager"
]
