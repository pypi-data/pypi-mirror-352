"""
缓存功能模块

提供内存和Redis缓存支持，支持全局配置和实例级配置
"""

from .config import CacheConfig
from .manager import CacheManager
from .backends import MemoryBackend, RedisBackend
from .global_config import (
    GlobalCacheManager,
    init_global_cache,
    get_cache_manager,
    get_global_cache_stats,
    global_cache_health_check
)

__all__ = [
    "CacheConfig",
    "CacheManager",
    "MemoryBackend",
    "RedisBackend",
    "GlobalCacheManager",
    "init_global_cache",
    "get_cache_manager",
    "get_global_cache_stats",
    "global_cache_health_check"
]
