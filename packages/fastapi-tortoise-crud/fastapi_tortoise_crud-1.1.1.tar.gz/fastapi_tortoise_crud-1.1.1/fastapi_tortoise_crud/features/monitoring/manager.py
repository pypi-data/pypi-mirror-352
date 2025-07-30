"""
监控管理器

统一管理监控功能
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .config import MonitoringConfig
from .metrics import MetricsCollector
from .middleware import (
    DatabaseMonitoringMixin, 
    CacheMonitoringMixin, 
    HookMonitoringMixin
)

logger = logging.getLogger(__name__)


class MonitoringManager:
    """
    监控管理器
    
    统一管理所有监控功能
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        初始化监控管理器
        
        Args:
            config: 监控配置
        """
        self.config = config
        self._enabled = config.enabled
        
        # 初始化组件
        self.metrics = MetricsCollector(config) if self._enabled else None
        self.db_monitor = DatabaseMonitoringMixin(self.metrics) if self._enabled else None
        self.cache_monitor = CacheMonitoringMixin(self.metrics) if self._enabled else None
        self.hook_monitor = HookMonitoringMixin(self.metrics) if self._enabled else None
        
        # 报告任务
        self._report_task = None
        self._cleanup_task = None
        
        if self._enabled:
            # 延迟启动后台任务，避免在同步上下文中创建
            self._tasks_started = False
    
    @property
    def enabled(self) -> bool:
        """监控是否启用"""
        return self._enabled
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        if self._tasks_started:
            return

        try:
            if self.config.enable_reports:
                self._report_task = asyncio.create_task(self._report_loop())

            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._tasks_started = True
        except RuntimeError:
            # 如果没有事件循环，跳过后台任务
            logger.warning("无法启动监控后台任务：没有运行的事件循环")
    
    async def _report_loop(self):
        """报告循环"""
        while True:
            try:
                await asyncio.sleep(self.config.report_interval_minutes * 60)
                await self._generate_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"报告生成失败: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                if self.metrics:
                    self.metrics.cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"数据清理失败: {e}")
    
    async def _generate_report(self):
        """生成监控报告"""
        if not self.metrics:
            return
        
        try:
            report = self.get_performance_report()
            logger.info(f"监控报告: {report}")
            
            # 检查阈值告警
            await self._check_alerts(report)
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
    
    async def _check_alerts(self, report: Dict[str, Any]):
        """检查告警条件"""
        alerts = []
        
        # 检查响应时间
        if "performance" in report:
            avg_response_time = report["performance"].get("avg_response_time_ms", 0)
            if avg_response_time > self.config.response_time_threshold_ms:
                alerts.append(f"平均响应时间过高: {avg_response_time:.2f}ms")
        
        # 检查错误率
        if "errors" in report:
            error_rate = report["errors"].get("error_rate_percent", 0)
            if error_rate > self.config.error_rate_threshold_percent:
                alerts.append(f"错误率过高: {error_rate:.2f}%")
        

        
        # 记录告警
        for alert in alerts:
            logger.warning(f"监控告警: {alert}")
            if self.metrics:
                self.metrics.increment_counter("monitoring_alerts_total", labels={"type": "threshold"})
    
    async def ensure_tasks_started(self):
        """确保后台任务已启动"""
        if self._enabled and not self._tasks_started:
            await self._start_background_tasks()

    def record_request(self, method: str, path: str, duration: float, status_code: int):
        """记录HTTP请求"""
        if not self.metrics:
            return

        labels = {"method": method, "path": path, "status": str(status_code)}

        self.metrics.observe_histogram("http_request_duration_seconds", duration, labels)
        self.metrics.increment_counter("http_requests_total", labels=labels)

        if status_code >= 400:
            self.metrics.increment_counter("http_errors_total", labels=labels)
    
    def record_database_query(self, query_type: str, duration: float, table: str = None, success: bool = True):
        """记录数据库查询"""
        if self.db_monitor:
            self.db_monitor.record_query(query_type, duration, table, success)
    
    def record_cache_operation(self, operation: str, hit: bool = None, duration: float = None):
        """记录缓存操作"""
        if self.cache_monitor:
            self.cache_monitor.record_cache_operation(operation, hit, duration)
    
    def record_hook_execution(self, stage: str, hook_name: str, duration: float, success: bool = True):
        """记录Hook执行"""
        if self.hook_monitor:
            self.hook_monitor.record_hook_execution(stage, hook_name, duration, success)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        if not self._enabled or not self.metrics:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "config": {
                "retention_hours": self.config.metrics_retention_hours,
                "aggregation_interval": self.config.aggregation_interval_seconds,
                "enable_reports": self.config.enable_reports
            },
            "metrics": self.metrics.get_all_metrics(),
            "thresholds": {
                "response_time_ms": self.config.response_time_threshold_ms,
                "error_rate_percent": self.config.error_rate_threshold_percent
            }
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.metrics:
            return {"enabled": False}
        
        # 获取最近一小时的数据
        since = datetime.now() - timedelta(hours=1)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "period": "last_hour",
            "performance": {},
            "errors": {},
            "system": {},
            "cache": {},
            "database": {},
            "hooks": {}
        }
        
        try:
            # 性能指标
            response_times = self.metrics.get_timeseries("http_request_duration_milliseconds", since=since)
            if response_times:
                durations = [p.value for p in response_times]
                report["performance"] = {
                    "total_requests": len(durations),
                    "avg_response_time_ms": sum(durations) / len(durations),
                    "min_response_time_ms": min(durations),
                    "max_response_time_ms": max(durations),
                    "p95_response_time_ms": self.metrics._percentile(durations, 95),
                    "p99_response_time_ms": self.metrics._percentile(durations, 99)
                }
            
            # 错误统计
            total_requests = self.metrics.get_counter("http_requests_total")
            total_errors = self.metrics.get_counter("http_errors_total")
            
            if total_requests > 0:
                error_rate = (total_errors / total_requests) * 100
                report["errors"] = {
                    "total_errors": total_errors,
                    "total_requests": total_requests,
                    "error_rate_percent": error_rate
                }
            

            
            # 缓存统计
            cache_hits = self.metrics.get_counter("cache_hits_total")
            cache_misses = self.metrics.get_counter("cache_misses_total")
            
            if cache_hits or cache_misses:
                total_cache_ops = cache_hits + cache_misses
                hit_rate = (cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0
                
                report["cache"] = {
                    "hits": cache_hits,
                    "misses": cache_misses,
                    "hit_rate_percent": hit_rate,
                    "total_operations": total_cache_ops
                }
            
            # 数据库统计
            db_queries = self.metrics.get_counter("db_queries_total")
            db_errors = self.metrics.get_counter("db_query_errors_total")
            
            if db_queries:
                report["database"] = {
                    "total_queries": db_queries,
                    "query_errors": db_errors,
                    "error_rate_percent": (db_errors / db_queries * 100) if db_queries > 0 else 0
                }
            
            # Hook统计
            hook_executions = self.metrics.get_counter("hook_executions_total")
            hook_errors = self.metrics.get_counter("hook_execution_errors_total")
            
            if hook_executions:
                report["hooks"] = {
                    "total_executions": hook_executions,
                    "execution_errors": hook_errors,
                    "error_rate_percent": (hook_errors / hook_executions * 100) if hook_executions > 0 else 0
                }
            
        except Exception as e:
            logger.error(f"生成性能报告失败: {e}")
            report["error"] = str(e)
        
        return report
    
    def export_prometheus_metrics(self) -> str:
        """导出Prometheus格式指标"""
        if not self.metrics:
            return ""
        
        return self.metrics.export_prometheus_format()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        if not self._enabled:
            return {
                "status": "disabled",
                "message": "监控未启用"
            }
        
        try:
            # 检查各组件状态
            health = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "metrics_collector": "healthy" if self.metrics else "disabled",
                    "database_monitor": "healthy" if self.db_monitor else "disabled",
                    "cache_monitor": "healthy" if self.cache_monitor else "disabled",
                    "hook_monitor": "healthy" if self.hook_monitor else "disabled"
                },
                "background_tasks": {
                    "report_task": "running" if self._report_task and not self._report_task.done() else "stopped",
                    "cleanup_task": "running" if self._cleanup_task and not self._cleanup_task.done() else "stopped"
                }
            }
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def shutdown(self):
        """关闭监控管理器"""
        if self._report_task:
            self._report_task.cancel()
            try:
                await self._report_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


__all__ = ["MonitoringManager"]
