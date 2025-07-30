"""
缓存管理器

统一的缓存操作接口
"""

import asyncio
import logging
import warnings
from typing import Any, Optional, Dict, List
from .config import CacheConfig
from .backends import MemoryBackend, RedisBackend, REDIS_AVAILABLE

logger = logging.getLogger(__name__)


class CacheManager:
    """
    缓存管理器
    
    提供统一的缓存操作接口，支持多种后端
    """
    
    def __init__(self, config: CacheConfig):
        """
        初始化缓存管理器
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self.backend = None
        self._enabled = config.enabled
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
        if self._enabled:
            self._init_backend()
    
    def _init_backend(self):
        """初始化缓存后端"""
        try:
            if self.config.backend == "redis":
                # 检查 Redis 是否可用
                if not REDIS_AVAILABLE:
                    warning_msg = (
                        "配置使用 Redis 缓存，但 redis 包未安装。"
                        "请安装: pip install fastapi-tortoise-crud[redis] "
                        "或 pip install redis>=4.0.0"
                    )
                    warnings.warn(warning_msg, UserWarning, stacklevel=3)
                    logger.warning(f"⚠️  {warning_msg}")

                self.backend = RedisBackend(self.config)
            else:
                self.backend = MemoryBackend(self.config)

            logger.info(f"✅ {self.config.backend.title()}缓存已启用")

        except Exception as e:
            logger.error(f"❌ 缓存初始化失败: {e}")
            if self.config.backend == "redis":
                # Redis失败时降级到内存缓存
                logger.info("🔄 降级到内存缓存")
                try:
                    self.backend = MemoryBackend(self.config)
                    logger.info("✅ 内存缓存已启用")
                except Exception as fallback_error:
                    logger.error(f"❌ 内存缓存也失败: {fallback_error}")
                    self._enabled = False
            else:
                self._enabled = False
    
    @property
    def enabled(self) -> bool:
        """缓存是否启用"""
        return self._enabled and self.backend is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        if not self.enabled:
            return None
        
        try:
            value = await self.backend.get(key)
            if value is not None:
                self._stats["hits"] += 1
                if self.config.enable_metrics:
                    logger.debug(f"缓存命中: {key}")
            else:
                self._stats["misses"] += 1
                if self.config.enable_metrics:
                    logger.debug(f"缓存未命中: {key}")
            
            return value
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"缓存获取失败 {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        if not self.enabled:
            return False
        
        # 检查是否缓存空值
        if value is None and not self.config.cache_null_values:
            return False
        
        try:
            ttl = ttl or (
                self.config.null_value_ttl if value is None 
                else self.config.default_ttl
            )
            
            success = await self.backend.set(key, value, ttl)
            if success:
                self._stats["sets"] += 1
                if self.config.enable_metrics:
                    logger.debug(f"缓存设置: {key} (TTL: {ttl}s)")
            
            return success
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"缓存设置失败 {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if not self.enabled:
            return False
        
        try:
            success = await self.backend.delete(key)
            if success:
                self._stats["deletes"] += 1
                if self.config.enable_metrics:
                    logger.debug(f"缓存删除: {key}")
            
            return success
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"缓存删除失败 {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        按模式删除缓存
        
        Args:
            pattern: 匹配模式
            
        Returns:
            删除的数量
        """
        if not self.enabled:
            return 0
        
        try:
            count = await self.backend.delete_pattern(pattern)
            self._stats["deletes"] += count
            if self.config.enable_metrics:
                logger.debug(f"批量删除缓存: {pattern} ({count}个)")
            
            return count
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"批量删除缓存失败 {pattern}: {e}")
            return 0
    
    async def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否清空成功
        """
        if not self.enabled:
            return False
        
        try:
            success = await self.backend.clear()
            if success and self.config.enable_metrics:
                logger.info("缓存已清空")
            
            return success
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"清空缓存失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        if not self.enabled:
            return False
        
        try:
            return await self.backend.exists(key)
        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        获取缓存剩余时间
        
        Args:
            key: 缓存键
            
        Returns:
            剩余时间（秒）或None
        """
        if not self.enabled:
            return None
        
        try:
            return await self.backend.get_ttl(key)
        except Exception as e:
            logger.error(f"获取缓存TTL失败 {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        total_operations = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_operations * 100) 
            if total_operations > 0 else 0
        )
        
        stats = {
            "enabled": self.enabled,
            "backend": self.config.backend if self.enabled else None,
            "hit_rate": round(hit_rate, 2),
            "operations": {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "errors": self._stats["errors"]
            },
            "config": {
                "default_ttl": self.config.default_ttl,
                "key_prefix": self.config.key_prefix,
                "serializer": self.config.serializer
            }
        }
        
        # 添加后端特定统计
        if self.enabled and hasattr(self.backend, 'get_stats'):
            stats["backend_stats"] = self.backend.get_stats()
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "缓存未启用"
            }
        
        try:
            # 测试基本操作
            test_key = f"{self.config.key_prefix}health_check"
            test_value = "ok"
            
            await self.set(test_key, test_value, 10)
            retrieved = await self.get(test_key)
            await self.delete(test_key)
            
            if retrieved == test_value:
                return {
                    "status": "healthy",
                    "backend": self.config.backend,
                    "message": "缓存工作正常"
                }
            else:
                return {
                    "status": "unhealthy",
                    "backend": self.config.backend,
                    "message": "缓存读写测试失败"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "backend": self.config.backend,
                "message": f"缓存健康检查失败: {e}"
            }


__all__ = ["CacheManager"]
