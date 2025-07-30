"""
全局缓存配置管理器

支持全局配置和实例级配置的优先级管理
"""

import logging
from typing import Optional, Dict, Any
from .config import CacheConfig
from .manager import CacheManager

logger = logging.getLogger(__name__)


class GlobalCacheManager:
    """
    全局缓存管理器
    
    管理全局缓存配置和实例
    """
    
    _instance: Optional['GlobalCacheManager'] = None
    _global_config: Optional[CacheConfig] = None
    _global_cache_manager: Optional[CacheManager] = None
    _instance_managers: Dict[str, CacheManager] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_global_config(cls, config: CacheConfig) -> CacheManager:
        """
        设置全局缓存配置
        
        Args:
            config: 缓存配置
            
        Returns:
            CacheManager: 全局缓存管理器实例
        """
        cls._global_config = config
        cls._global_cache_manager = CacheManager(config)
        
        logger.info(f"✅ 全局缓存配置已设置: {config.backend}")
        return cls._global_cache_manager
    
    @classmethod
    def get_global_config(cls) -> Optional[CacheConfig]:
        """获取全局缓存配置"""
        return cls._global_config
    
    @classmethod
    def get_global_manager(cls) -> Optional[CacheManager]:
        """获取全局缓存管理器"""
        return cls._global_cache_manager
    
    @classmethod
    def get_or_create_manager(
        cls,
        instance_config: Optional[CacheConfig] = None,
        instance_id: str = "default",
        **override_params
    ) -> Optional[CacheManager]:
        """
        获取或创建缓存管理器

        优先级：实例配置 > 全局配置 + 覆盖参数 > 全局配置 > None

        Args:
            instance_config: 实例级配置（优先级最高）
            instance_id: 实例ID，用于缓存管理器复用
            **override_params: 覆盖参数（如 default_ttl=200）

        Returns:
            Optional[CacheManager]: 缓存管理器实例
        """
        # 如果有实例配置，优先使用
        if instance_config:
            # 生成配置键用于复用
            config_key = cls._generate_config_key(instance_config, instance_id)

            if config_key not in cls._instance_managers:
                cls._instance_managers[config_key] = CacheManager(instance_config)
                logger.debug(f"🔧 创建实例缓存管理器: {instance_id}")

            return cls._instance_managers[config_key]

        # 如果有全局配置
        if cls._global_config:
            # 如果有覆盖参数，创建新的配置
            if override_params:
                # 复制全局配置并应用覆盖参数
                merged_config = cls._merge_config(cls._global_config, override_params)
                config_key = cls._generate_config_key(merged_config, instance_id)

                if config_key not in cls._instance_managers:
                    cls._instance_managers[config_key] = CacheManager(merged_config)
                    logger.debug(f"🔧 创建合并配置缓存管理器: {instance_id}")

                return cls._instance_managers[config_key]
            else:
                # 使用全局缓存管理器
                logger.debug(f"🌐 使用全局缓存管理器: {instance_id}")
                return cls._global_cache_manager

        # 都没有配置，返回None
        logger.debug(f"❌ 无缓存配置: {instance_id}")
        return None
    
    @classmethod
    def _merge_config(cls, base_config: CacheConfig, override_params: dict) -> CacheConfig:
        """
        合并配置参数

        Args:
            base_config: 基础配置
            override_params: 覆盖参数

        Returns:
            CacheConfig: 合并后的配置
        """
        # 将基础配置转换为字典
        config_dict = {
            'enabled': base_config.enabled,
            'backend': base_config.backend,
            'default_ttl': base_config.default_ttl,
            'key_prefix': base_config.key_prefix,
            'serializer': base_config.serializer,
            'max_memory_items': base_config.max_memory_items,
            'redis_url': base_config.redis_url,
            'redis_pool_size': base_config.redis_pool_size,
            'redis_timeout': base_config.redis_timeout,
            'enable_compression': base_config.enable_compression,
            'compression_threshold': base_config.compression_threshold,
            'cache_null_values': base_config.cache_null_values,
            'null_value_ttl': base_config.null_value_ttl,
            'enable_metrics': base_config.enable_metrics,
            'metrics_interval': base_config.metrics_interval
        }

        # 应用覆盖参数
        config_dict.update(override_params)

        # 创建新的配置对象
        return CacheConfig(**config_dict)

    @classmethod
    def _generate_config_key(cls, config: CacheConfig, instance_id: str) -> str:
        """生成配置键"""
        return f"{instance_id}:{config.backend}:{config.default_ttl}:{config.max_memory_items}:{config.redis_url}"
    
    @classmethod
    def clear_instance_managers(cls):
        """清空实例管理器缓存"""
        cls._instance_managers.clear()
        logger.info("🧹 实例缓存管理器已清空")
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取全局缓存统计"""
        stats = {
            "global_config_set": cls._global_config is not None,
            "global_manager_active": cls._global_cache_manager is not None,
            "instance_managers_count": len(cls._instance_managers),
            "instance_managers": {}
        }
        
        # 全局管理器统计
        if cls._global_cache_manager:
            stats["global_manager"] = cls._global_cache_manager.get_stats()
        
        # 实例管理器统计
        for key, manager in cls._instance_managers.items():
            stats["instance_managers"][key] = manager.get_stats()
        
        return stats
    
    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """全局健康检查"""
        health = {
            "global_cache": "disabled",
            "instance_caches": {},
            "total_managers": len(cls._instance_managers)
        }
        
        # 检查全局缓存
        if cls._global_cache_manager:
            global_health = await cls._global_cache_manager.health_check()
            health["global_cache"] = global_health["status"]
        
        # 检查实例缓存
        for key, manager in cls._instance_managers.items():
            instance_health = await manager.health_check()
            health["instance_caches"][key] = instance_health["status"]
        
        return health
    
    @classmethod
    async def shutdown_all(cls):
        """关闭所有缓存管理器"""
        # 关闭全局管理器
        if cls._global_cache_manager:
            # 这里可以添加关闭逻辑，如果需要的话
            pass
        
        # 关闭实例管理器
        for manager in cls._instance_managers.values():
            # 这里可以添加关闭逻辑，如果需要的话
            pass
        
        cls._instance_managers.clear()
        cls._global_cache_manager = None
        cls._global_config = None
        
        logger.info("🔒 所有缓存管理器已关闭")


# 便捷函数
def init_global_cache(config: CacheConfig) -> CacheManager:
    """
    初始化全局缓存
    
    Args:
        config: 缓存配置
        
    Returns:
        CacheManager: 全局缓存管理器
    """
    return GlobalCacheManager.set_global_config(config)


def get_cache_manager(
    instance_config: Optional[CacheConfig] = None,
    instance_id: str = "default",
    **override_params
) -> Optional[CacheManager]:
    """
    获取缓存管理器

    Args:
        instance_config: 实例配置（可选）
        instance_id: 实例ID
        **override_params: 覆盖参数（如 default_ttl=200）

    Returns:
        Optional[CacheManager]: 缓存管理器实例
    """
    return GlobalCacheManager.get_or_create_manager(instance_config, instance_id, **override_params)


def get_global_cache_stats() -> Dict[str, Any]:
    """获取全局缓存统计"""
    return GlobalCacheManager.get_stats()


async def global_cache_health_check() -> Dict[str, Any]:
    """全局缓存健康检查"""
    return await GlobalCacheManager.health_check()


__all__ = [
    "GlobalCacheManager",
    "init_global_cache",
    "get_cache_manager", 
    "get_global_cache_stats",
    "global_cache_health_check"
]
