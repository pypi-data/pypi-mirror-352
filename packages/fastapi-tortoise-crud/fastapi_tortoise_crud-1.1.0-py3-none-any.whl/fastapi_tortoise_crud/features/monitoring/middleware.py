"""
监控中间件

自动收集HTTP请求指标
"""

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .metrics import MetricsCollector
from .config import MonitoringConfig


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    监控中间件
    
    自动收集HTTP请求的性能指标
    """
    
    def __init__(self, app, config: MonitoringConfig, metrics_collector: MetricsCollector):
        """
        初始化监控中间件
        
        Args:
            app: ASGI应用
            config: 监控配置
            metrics_collector: 指标收集器
        """
        super().__init__(app)
        self.config = config
        self.metrics = metrics_collector
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并收集指标"""
        if not self.config.enabled or not self.config.enable_request_metrics:
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        
        # 增加请求计数
        self.metrics.increment_counter(
            "http_requests_total",
            labels={"method": method, "path": path}
        )
        
        # 增加并发请求数
        self.metrics.increment_counter("http_requests_in_progress")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 记录响应状态
            status_code = response.status_code
            status_class = f"{status_code // 100}xx"
            
            # 计算响应时间
            duration = time.time() - start_time
            duration_ms = duration * 1000
            
            # 记录响应时间
            self.metrics.observe_histogram(
                "http_request_duration_seconds",
                duration,
                labels={"method": method, "path": path, "status": str(status_code)}
            )
            
            self.metrics.observe_histogram(
                "http_request_duration_milliseconds",
                duration_ms,
                labels={"method": method, "path": path, "status": str(status_code)}
            )
            
            # 记录响应状态计数
            self.metrics.increment_counter(
                "http_responses_total",
                labels={
                    "method": method,
                    "path": path,
                    "status": str(status_code),
                    "status_class": status_class
                }
            )
            
            # 检查响应时间阈值
            if duration_ms > self.config.response_time_threshold_ms:
                self.metrics.increment_counter(
                    "http_slow_requests_total",
                    labels={"method": method, "path": path}
                )
            
            # 记录错误
            if status_code >= 400:
                self.metrics.increment_counter(
                    "http_errors_total",
                    labels={
                        "method": method,
                        "path": path,
                        "status": str(status_code),
                        "status_class": status_class
                    }
                )
            
            return response
            
        except Exception as e:
            # 记录异常
            duration = time.time() - start_time
            
            self.metrics.increment_counter(
                "http_exceptions_total",
                labels={
                    "method": method,
                    "path": path,
                    "exception": type(e).__name__
                }
            )
            
            self.metrics.observe_histogram(
                "http_request_duration_seconds",
                duration,
                labels={"method": method, "path": path, "status": "exception"}
            )
            
            raise e
            
        finally:
            # 减少并发请求数
            self.metrics.increment_counter("http_requests_in_progress", -1)


class DatabaseMonitoringMixin:
    """数据库监控混入类"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_query(self, query_type: str, duration: float, table: str = None, success: bool = True):
        """记录数据库查询"""
        labels = {"type": query_type, "success": str(success)}
        if table:
            labels["table"] = table
        
        self.metrics.observe_histogram("db_query_duration_seconds", duration, labels)
        self.metrics.increment_counter("db_queries_total", labels=labels)
        
        if not success:
            self.metrics.increment_counter("db_query_errors_total", labels=labels)
    
    def record_connection_pool_stats(self, active: int, idle: int, total: int):
        """记录连接池统计"""
        self.metrics.set_gauge("db_connections_active", active)
        self.metrics.set_gauge("db_connections_idle", idle)
        self.metrics.set_gauge("db_connections_total", total)


class CacheMonitoringMixin:
    """缓存监控混入类"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_cache_operation(self, operation: str, hit: bool = None, duration: float = None):
        """记录缓存操作"""
        labels = {"operation": operation}
        
        if hit is not None:
            labels["result"] = "hit" if hit else "miss"
            
            if hit:
                self.metrics.increment_counter("cache_hits_total", labels={"operation": operation})
            else:
                self.metrics.increment_counter("cache_misses_total", labels={"operation": operation})
        
        self.metrics.increment_counter("cache_operations_total", labels=labels)
        
        if duration is not None:
            self.metrics.observe_histogram("cache_operation_duration_seconds", duration, labels)
    
    def record_cache_size(self, size: int, max_size: int = None):
        """记录缓存大小"""
        self.metrics.set_gauge("cache_size", size)
        if max_size:
            self.metrics.set_gauge("cache_max_size", max_size)
            self.metrics.set_gauge("cache_usage_ratio", size / max_size)


class HookMonitoringMixin:
    """Hook监控混入类"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_hook_execution(self, stage: str, hook_name: str, duration: float, success: bool = True):
        """记录Hook执行"""
        labels = {
            "stage": stage,
            "hook": hook_name,
            "success": str(success)
        }
        
        self.metrics.observe_histogram("hook_execution_duration_seconds", duration, labels)
        self.metrics.increment_counter("hook_executions_total", labels=labels)
        
        if not success:
            self.metrics.increment_counter("hook_execution_errors_total", labels=labels)
    
    def record_hook_stage_stats(self, stage: str, total_hooks: int, enabled_hooks: int):
        """记录Hook阶段统计"""
        labels = {"stage": stage}
        self.metrics.set_gauge("hooks_total", total_hooks, labels)
        self.metrics.set_gauge("hooks_enabled", enabled_hooks, labels)


def create_monitoring_middleware(config: MonitoringConfig, metrics_collector: MetricsCollector):
    """
    创建监控中间件
    
    Args:
        config: 监控配置
        metrics_collector: 指标收集器
        
    Returns:
        MonitoringMiddleware: 监控中间件实例
    """
    return lambda app: MonitoringMiddleware(app, config, metrics_collector)


__all__ = [
    "MonitoringMiddleware",
    "DatabaseMonitoringMixin",
    "CacheMonitoringMixin", 
    "HookMonitoringMixin",
    "create_monitoring_middleware"
]
