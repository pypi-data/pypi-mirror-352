"""
缓存配置
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class CacheConfig:
    """缓存配置类"""
    
    # 基础配置
    enabled: bool = True
    backend: str = "memory"  # memory 或 redis
    default_ttl: int = 3600  # 默认过期时间（秒）
    key_prefix: str = "fastapi_crud:"
    
    # 序列化配置
    serializer: str = "pickle"  # json 或 pickle
    
    # 内存缓存配置
    max_memory_items: int = 1000
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10
    redis_timeout: int = 5
    
    # 高级配置
    enable_compression: bool = False
    compression_threshold: int = 1024  # 字节
    
    # 缓存策略
    cache_null_values: bool = False
    null_value_ttl: int = 60
    
    # 监控配置
    enable_metrics: bool = True
    metrics_interval: int = 60  # 秒
    
    def __post_init__(self):
        """配置验证"""
        if self.backend not in ["memory", "redis"]:
            raise ValueError("backend must be 'memory' or 'redis'")
        
        if self.serializer not in ["json", "pickle"]:
            raise ValueError("serializer must be 'json' or 'pickle'")
        
        if self.default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        
        if self.max_memory_items <= 0:
            raise ValueError("max_memory_items must be positive")


# 预定义配置
class CachePresets:
    """缓存预设配置"""
    
    @staticmethod
    def memory_default() -> CacheConfig:
        """默认内存缓存配置"""
        return CacheConfig(
            backend="memory",
            max_memory_items=1000,
            default_ttl=3600
        )
    
    @staticmethod
    def memory_large() -> CacheConfig:
        """大容量内存缓存配置"""
        return CacheConfig(
            backend="memory",
            max_memory_items=10000,
            default_ttl=7200
        )
    
    @staticmethod
    def redis_default() -> CacheConfig:
        """默认Redis缓存配置"""
        return CacheConfig(
            backend="redis",
            redis_url="redis://localhost:6379/0",
            default_ttl=3600
        )
    
    @staticmethod
    def redis_cluster() -> CacheConfig:
        """Redis集群配置"""
        return CacheConfig(
            backend="redis",
            redis_url="redis://localhost:6379/0",
            redis_pool_size=20,
            default_ttl=7200,
            enable_compression=True
        )
    
    @staticmethod
    def development() -> CacheConfig:
        """开发环境配置"""
        return CacheConfig(
            backend="memory",
            max_memory_items=100,
            default_ttl=300,  # 5分钟
            enable_metrics=True
        )
    
    @staticmethod
    def production() -> CacheConfig:
        """生产环境配置"""
        return CacheConfig(
            backend="redis",
            redis_url="redis://localhost:6379/0",
            redis_pool_size=20,
            default_ttl=3600,
            enable_compression=True,
            enable_metrics=True
        )


__all__ = ["CacheConfig", "CachePresets"]
