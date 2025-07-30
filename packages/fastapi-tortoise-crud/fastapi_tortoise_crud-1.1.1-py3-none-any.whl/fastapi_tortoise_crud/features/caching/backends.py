"""
缓存后端实现

支持内存和Redis缓存
"""

import json
import pickle
import time
import threading
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from collections import OrderedDict

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None
    import warnings

from .config import CacheConfig


class CacheBackend(ABC):
    """缓存后端抽象基类"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass
    
    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[int]:
        """获取缓存剩余时间"""
        pass
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize(self, data: Any) -> bytes:
        """序列化数据"""
        if self.config.serializer == "pickle":
            return pickle.dumps(data)
        else:
            # JSON序列化
            try:
                return json.dumps(data, default=self._json_serializer, ensure_ascii=False).encode('utf-8')
            except Exception:
                # 如果JSON失败，使用pickle作为后备
                return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """反序列化数据"""
        if self.config.serializer == "pickle":
            return pickle.loads(data)
        else:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                # 尝试pickle反序列化
                try:
                    return pickle.loads(data)
                except Exception:
                    return None
    
    def _json_serializer(self, obj):
        """自定义JSON序列化器"""
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            try:
                result = {}
                for key, value in obj.__dict__.items():
                    if not key.startswith('_'):
                        if hasattr(value, 'model_dump'):
                            result[key] = value.model_dump()
                        elif hasattr(value, 'dict'):
                            result[key] = value.dict()
                        elif isinstance(value, (list, tuple)):
                            result[key] = [
                                item.model_dump() if hasattr(item, 'model_dump')
                                else item.dict() if hasattr(item, 'dict')
                                else str(item)
                                for item in value
                            ]
                        else:
                            result[key] = str(value)
                return result
            except:
                return str(obj)
        else:
            return str(obj)


class MemoryBackend(CacheBackend):
    """内存缓存后端"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: OrderedDict = OrderedDict()
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._max_items = config.max_memory_items
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._make_key(key)
        
        with self._lock:
            # 检查是否过期
            if cache_key in self._expiry and time.time() > self._expiry[cache_key]:
                self._remove(cache_key)
                return None
            
            if cache_key in self._cache:
                # LRU: 移动到末尾
                value = self._cache.pop(cache_key)
                self._cache[cache_key] = value
                return value
            
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """设置缓存值"""
        cache_key = self._make_key(key)
        
        with self._lock:
            # 如果缓存已满，删除最旧的项
            if len(self._cache) >= self._max_items and cache_key not in self._cache:
                oldest_key = next(iter(self._cache))
                self._remove(oldest_key)
            
            self._cache[cache_key] = value
            
            # 设置过期时间
            if ttl > 0:
                self._expiry[cache_key] = time.time() + ttl
            elif cache_key in self._expiry:
                del self._expiry[cache_key]
            
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        cache_key = self._make_key(key)
        
        with self._lock:
            return self._remove(cache_key)
    
    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        cache_pattern = self._make_key(pattern.replace("*", ""))
        deleted_count = 0
        
        with self._lock:
            keys_to_delete = []
            for key in self._cache.keys():
                if key.startswith(cache_pattern):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                if self._remove(key):
                    deleted_count += 1
        
        return deleted_count
    
    async def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
            return True
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_key = self._make_key(key)
        
        with self._lock:
            # 检查是否过期
            if cache_key in self._expiry and time.time() > self._expiry[cache_key]:
                self._remove(cache_key)
                return False
            
            return cache_key in self._cache
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """获取缓存剩余时间"""
        cache_key = self._make_key(key)
        
        with self._lock:
            if cache_key not in self._cache:
                return None
            
            if cache_key in self._expiry:
                remaining = self._expiry[cache_key] - time.time()
                return max(0, int(remaining))
            
            return -1  # 永不过期
    
    def _remove(self, key: str) -> bool:
        """内部删除方法"""
        removed = False
        if key in self._cache:
            del self._cache[key]
            removed = True
        if key in self._expiry:
            del self._expiry[key]
        return removed
    
    def cleanup_expired(self):
        """清理过期项"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, expiry_time in self._expiry.items()
                if current_time > expiry_time
            ]
            for key in expired_keys:
                self._remove(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取后端统计信息"""
        with self._lock:
            return {
                "type": "memory",
                "total_items": len(self._cache),
                "max_items": self._max_items,
                "expired_items": len(self._expiry),
                "memory_usage": f"{len(self._cache)}/{self._max_items}"
            }


class RedisBackend(CacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)

        if not REDIS_AVAILABLE:
            error_msg = (
                "Redis 缓存后端不可用。请安装 redis 依赖：\n"
                "pip install fastapi-tortoise-crud[redis]\n"
                "或者\n"
                "pip install redis>=4.0.0"
            )
            raise ImportError(error_msg)
        
        self._redis = redis.from_url(
            config.redis_url,
            max_connections=config.redis_pool_size,
            socket_timeout=config.redis_timeout,
            decode_responses=False  # 我们需要处理bytes
        )
        
        # 测试连接
        self._redis.ping()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._make_key(key)
        
        try:
            data = self._redis.get(cache_key)
            if data:
                return self._deserialize(data)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """设置缓存值"""
        cache_key = self._make_key(key)
        
        try:
            serialized_data = self._serialize(value)
            return self._redis.setex(cache_key, ttl, serialized_data)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        cache_key = self._make_key(key)
        
        try:
            return bool(self._redis.delete(cache_key))
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        cache_pattern = self._make_key(pattern)
        
        try:
            keys = self._redis.keys(cache_pattern)
            if keys:
                return self._redis.delete(*keys)
            return 0
        except Exception:
            return 0
    
    async def clear(self) -> bool:
        """清空缓存"""
        try:
            pattern = self._make_key("*")
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_key = self._make_key(key)
        
        try:
            return bool(self._redis.exists(cache_key))
        except Exception:
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """获取缓存剩余时间"""
        cache_key = self._make_key(key)
        
        try:
            ttl = self._redis.ttl(cache_key)
            return ttl if ttl > 0 else None
        except Exception:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取后端统计信息"""
        try:
            info = self._redis.info()
            return {
                "type": "redis",
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception:
            return {"type": "redis", "error": "无法获取Redis统计信息"}


__all__ = ["CacheBackend", "MemoryBackend", "RedisBackend"]
