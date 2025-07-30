"""
指标收集器

收集和管理各种性能指标
"""

import time
import threading
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .config import MonitoringConfig


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """指标摘要"""
    name: str
    count: int
    sum: float
    min: float
    max: float
    avg: float
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    指标收集器
    
    收集和管理各种性能指标
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        初始化指标收集器
        
        Args:
            config: 监控配置
        """
        self.config = config
        self._enabled = config.enabled and config.enable_metrics
        self._lock = threading.RLock()
        
        # 指标存储
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timeseries: Dict[str, deque] = defaultdict(lambda: deque(maxlen=config.max_metrics_records))
        
        # 标签存储
        self._labels: Dict[str, Dict[str, str]] = defaultdict(dict)
        
        # 聚合数据
        self._aggregated_data: Dict[str, Any] = {}
        self._last_aggregation = time.time()
    
    @property
    def enabled(self) -> bool:
        """指标收集是否启用"""
        return self._enabled
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """
        增加计数器
        
        Args:
            name: 指标名称
            value: 增加值
            labels: 标签
        """
        if not self._enabled:
            return
        
        with self._lock:
            full_name = self._get_metric_name(name, labels)
            self._counters[full_name] += value
            
            if labels:
                self._labels[full_name].update(labels)
            
            # 添加到时间序列
            self._add_to_timeseries(full_name, value)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        设置仪表值
        
        Args:
            name: 指标名称
            value: 值
            labels: 标签
        """
        if not self._enabled:
            return
        
        with self._lock:
            full_name = self._get_metric_name(name, labels)
            self._gauges[full_name] = value
            
            if labels:
                self._labels[full_name].update(labels)
            
            # 添加到时间序列
            self._add_to_timeseries(full_name, value)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        观察直方图值
        
        Args:
            name: 指标名称
            value: 观察值
            labels: 标签
        """
        if not self._enabled:
            return
        
        with self._lock:
            full_name = self._get_metric_name(name, labels)
            self._histograms[full_name].append(value)
            
            # 限制历史数据大小
            if len(self._histograms[full_name]) > self.config.max_metrics_records:
                self._histograms[full_name] = self._histograms[full_name][-self.config.max_metrics_records:]
            
            if labels:
                self._labels[full_name].update(labels)
            
            # 添加到时间序列
            self._add_to_timeseries(full_name, value)
    
    def time_function(self, name: str, labels: Dict[str, str] = None):
        """
        函数执行时间装饰器
        
        Args:
            name: 指标名称
            labels: 标签
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.observe_histogram(f"{name}_duration", duration, labels)
            return wrapper
        return decorator
    
    def _get_metric_name(self, name: str, labels: Dict[str, str] = None) -> str:
        """生成完整的指标名称"""
        if not labels:
            return name
        
        # 将标签排序后添加到名称中
        sorted_labels = sorted(labels.items())
        label_str = ",".join(f"{k}={v}" for k, v in sorted_labels)
        return f"{name}{{{label_str}}}"
    
    def _add_to_timeseries(self, name: str, value: float):
        """添加到时间序列"""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=self._labels.get(name, {}).copy()
        )
        self._timeseries[name].append(point)
    
    def get_counter(self, name: str, labels: Dict[str, str] = None) -> float:
        """获取计数器值"""
        full_name = self._get_metric_name(name, labels)
        return self._counters.get(full_name, 0.0)
    
    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> float:
        """获取仪表值"""
        full_name = self._get_metric_name(name, labels)
        return self._gauges.get(full_name, 0.0)
    
    def get_histogram_summary(self, name: str, labels: Dict[str, str] = None) -> Optional[MetricSummary]:
        """获取直方图摘要"""
        full_name = self._get_metric_name(name, labels)
        values = self._histograms.get(full_name, [])
        
        if not values:
            return None
        
        return MetricSummary(
            name=name,
            count=len(values),
            sum=sum(values),
            min=min(values),
            max=max(values),
            avg=sum(values) / len(values),
            labels=labels or {}
        )
    
    def get_timeseries(self, name: str, labels: Dict[str, str] = None, 
                      since: datetime = None) -> List[MetricPoint]:
        """获取时间序列数据"""
        full_name = self._get_metric_name(name, labels)
        points = list(self._timeseries.get(full_name, []))
        
        if since:
            points = [p for p in points if p.timestamp >= since]
        
        return points
    
    def aggregate_metrics(self) -> Dict[str, Any]:
        """聚合指标数据"""
        if not self._enabled:
            return {}
        
        current_time = time.time()
        if current_time - self._last_aggregation < self.config.aggregation_interval_seconds:
            return self._aggregated_data
        
        with self._lock:
            aggregated = {
                "timestamp": datetime.now().isoformat(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {}
            }
            
            # 聚合直方图数据
            for name, values in self._histograms.items():
                if values:
                    aggregated["histograms"][name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "p50": self._percentile(values, 50),
                        "p90": self._percentile(values, 90),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99)
                    }
            
            self._aggregated_data = aggregated
            self._last_aggregation = current_time
            
            return aggregated
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def cleanup_old_data(self):
        """清理过期数据"""
        if not self._enabled:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=self.config.metrics_retention_hours)
        
        with self._lock:
            # 清理时间序列数据
            for name, points in self._timeseries.items():
                # 过滤掉过期的数据点
                valid_points = [p for p in points if p.timestamp >= cutoff_time]
                self._timeseries[name] = deque(valid_points, maxlen=self.config.max_metrics_records)
            
            # 清理直方图数据（保留最近的数据）
            for name, values in self._histograms.items():
                if len(values) > self.config.max_metrics_records:
                    self._histograms[name] = values[-self.config.max_metrics_records:]
    
    def reset_metrics(self):
        """重置所有指标"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timeseries.clear()
            self._labels.clear()
            self._aggregated_data.clear()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        if not self._enabled:
            return {"enabled": False}
        
        with self._lock:
            return {
                "enabled": True,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: self.get_histogram_summary(name.split("{")[0], 
                                                   self._parse_labels(name))
                    for name in self._histograms.keys()
                },
                "aggregated": self._aggregated_data,
                "metadata": {
                    "total_metrics": len(self._counters) + len(self._gauges) + len(self._histograms),
                    "retention_hours": self.config.metrics_retention_hours,
                    "max_records": self.config.max_metrics_records
                }
            }
    
    def _parse_labels(self, metric_name: str) -> Dict[str, str]:
        """从指标名称中解析标签"""
        if "{" not in metric_name:
            return {}
        
        try:
            label_part = metric_name.split("{")[1].split("}")[0]
            labels = {}
            for pair in label_part.split(","):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    labels[key] = value
            return labels
        except:
            return {}
    
    def export_prometheus_format(self) -> str:
        """导出Prometheus格式的指标"""
        if not self._enabled:
            return ""
        
        lines = []
        
        # 导出计数器
        for name, value in self._counters.items():
            clean_name = name.split("{")[0]
            labels = self._parse_labels(name)
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            
            if label_str:
                lines.append(f'{clean_name}{{{label_str}}} {value}')
            else:
                lines.append(f'{clean_name} {value}')
        
        # 导出仪表
        for name, value in self._gauges.items():
            clean_name = name.split("{")[0]
            labels = self._parse_labels(name)
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            
            if label_str:
                lines.append(f'{clean_name}{{{label_str}}} {value}')
            else:
                lines.append(f'{clean_name} {value}')
        
        return "\n".join(lines)


__all__ = ["MetricsCollector", "MetricPoint", "MetricSummary"]
