"""
监控系统配置
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MonitoringConfig:
    """监控系统配置"""
    
    # 基础配置
    enabled: bool = True
    
    # 指标收集
    enable_metrics: bool = True
    enable_request_metrics: bool = True
    enable_cache_metrics: bool = True
    enable_hook_metrics: bool = True
    enable_database_metrics: bool = True
    
    # 性能监控
    enable_performance_tracking: bool = True
    track_response_times: bool = True
    
    # 错误监控
    enable_error_tracking: bool = True
    track_error_rates: bool = True
    track_error_details: bool = True
    
    # 数据保留
    metrics_retention_hours: int = 24
    max_metrics_records: int = 10000
    
    # 聚合配置
    enable_aggregation: bool = True
    aggregation_interval_seconds: int = 60
    
    # 报告配置
    enable_reports: bool = True
    report_interval_minutes: int = 15
    
    # 阈值配置
    response_time_threshold_ms: float = 1000.0
    error_rate_threshold_percent: float = 5.0
    
    # 导出配置
    enable_prometheus: bool = False
    prometheus_port: int = 9090
    
    # 自定义指标
    custom_metrics: List[str] = field(default_factory=list)
    
    # 标签配置
    default_labels: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """配置验证"""
        if self.metrics_retention_hours <= 0:
            raise ValueError("metrics_retention_hours must be positive")
        
        if self.max_metrics_records <= 0:
            raise ValueError("max_metrics_records must be positive")
        
        if self.aggregation_interval_seconds <= 0:
            raise ValueError("aggregation_interval_seconds must be positive")


# 预定义配置
class MonitoringPresets:
    """监控预设配置"""
    
    @staticmethod
    def basic() -> MonitoringConfig:
        """基础监控配置"""
        return MonitoringConfig(
            enable_metrics=True,
            enable_performance_tracking=True,
            enable_error_tracking=True,
            track_memory_usage=False,
            track_cpu_usage=False,
            enable_reports=False
        )
    
    @staticmethod
    def development() -> MonitoringConfig:
        """开发环境配置"""
        return MonitoringConfig(
            enable_metrics=True,
            enable_performance_tracking=True,
            enable_error_tracking=True,
            enable_reports=True,
            metrics_retention_hours=6,
            report_interval_minutes=5
        )
    
    @staticmethod
    def production() -> MonitoringConfig:
        """生产环境配置"""
        return MonitoringConfig(
            enable_metrics=True,
            enable_performance_tracking=True,
            enable_error_tracking=True,
            enable_reports=True,
            enable_prometheus=True,
            metrics_retention_hours=72,
            max_metrics_records=50000,
            response_time_threshold_ms=500.0,
            error_rate_threshold_percent=1.0
        )
    
    @staticmethod
    def performance() -> MonitoringConfig:
        """性能监控配置"""
        return MonitoringConfig(
            enable_metrics=True,
            enable_performance_tracking=True,
            enable_error_tracking=False,
            enable_reports=False,
            aggregation_interval_seconds=30,
            response_time_threshold_ms=100.0
        )
    
    @staticmethod
    def minimal() -> MonitoringConfig:
        """最小监控配置"""
        return MonitoringConfig(
            enable_metrics=True,
            enable_performance_tracking=False,
            enable_error_tracking=True,
            enable_reports=False,
            metrics_retention_hours=1,
            max_metrics_records=1000
        )


__all__ = ["MonitoringConfig", "MonitoringPresets"]
