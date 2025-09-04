"""Monitoring and metrics collection for OpenAGI."""

import logging
import time
import threading
import psutil
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric measurement."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    gpu_percent: Optional[float] = None
    gpu_memory_used: Optional[float] = None
    gpu_memory_total: Optional[float] = None


class MetricsCollector:
    """
    Collects and manages performance metrics for OpenAGI platform.
    
    Tracks:
    - System resource usage (CPU, memory, disk, network)
    - Model performance metrics
    - Agent execution statistics
    - API request metrics
    - Custom application metrics
    """
    
    def __init__(self, config):
        """Initialize metrics collector."""
        self.config = config
        self.enabled = config.get("openagi.monitoring.enabled", True)
        
        if not self.enabled:
            logger.info("Monitoring disabled")
            return
            
        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # System monitoring
        self._system_metrics = SystemMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self._monitoring_thread = None
        self._shutdown = False
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info("Metrics collector initialized")
        
    def _start_monitoring(self):
        """Start system monitoring thread."""
        if not self.enabled:
            return
            
        self._monitoring_thread = threading.Thread(target=self._monitor_system)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
        
    def _monitor_system(self):
        """Monitor system resources continuously."""
        while not self._shutdown:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used_gb = memory.used / (1024**3)
                memory_total_gb = memory.total / (1024**3)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                disk_used_gb = disk.used / (1024**3)
                disk_total_gb = disk.total / (1024**3)
                
                # Network usage
                network = psutil.net_io_counters()
                network_bytes_sent = network.bytes_sent
                network_bytes_recv = network.bytes_recv
                
                # GPU usage (if available)
                gpu_percent = None
                gpu_memory_used = None
                gpu_memory_total = None
                
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Use first GPU
                        gpu_percent = gpu.load * 100
                        gpu_memory_used = gpu.memoryUsed / 1024  # Convert to GB
                        gpu_memory_total = gpu.memoryTotal / 1024
                except ImportError:
                    pass  # GPU monitoring not available
                    
                # Update metrics
                self._system_metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_used_gb=memory_used_gb,
                    memory_total_gb=memory_total_gb,
                    disk_percent=disk_percent,
                    disk_used_gb=disk_used_gb,
                    disk_total_gb=disk_total_gb,
                    network_bytes_sent=network_bytes_sent,
                    network_bytes_recv=network_bytes_recv,
                    gpu_percent=gpu_percent,
                    gpu_memory_used=gpu_memory_used,
                    gpu_memory_total=gpu_memory_total
                )
                
                # Record time series
                timestamp = time.time()
                self.record_gauge("system.cpu_percent", cpu_percent, timestamp)
                self.record_gauge("system.memory_percent", memory_percent, timestamp)
                self.record_gauge("system.disk_percent", disk_percent, timestamp)
                
                if gpu_percent is not None:
                    self.record_gauge("system.gpu_percent", gpu_percent, timestamp)
                    self.record_gauge("system.gpu_memory_percent", 
                                    (gpu_memory_used / gpu_memory_total) * 100, timestamp)
                    
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(10)
                
    def record_gauge(self, metric_name: str, value: float, timestamp: float = None, 
                    labels: Dict[str, str] = None):
        """
        Record a gauge metric (instantaneous value).
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp: Optional timestamp (uses current time if None)
            labels: Optional metric labels
        """
        if not self.enabled:
            return
            
        timestamp = timestamp or time.time()
        labels = labels or {}
        
        point = MetricPoint(timestamp, value, labels)
        self.metrics[metric_name].append(point)
        
    def record_counter(self, metric_name: str, value: int = 1, labels: Dict[str, str] = None):
        """
        Record a counter metric (cumulative value).
        
        Args:
            metric_name: Name of the metric
            value: Amount to increment (default 1)
            labels: Optional metric labels
        """
        if not self.enabled:
            return
            
        self.counters[metric_name] += value
        
        # Also record as time series
        timestamp = time.time()
        point = MetricPoint(timestamp, self.counters[metric_name], labels or {})
        self.metrics[f"{metric_name}_total"].append(point)
        
    def record_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """
        Record a histogram metric (distribution of values).
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Optional metric labels
        """
        if not self.enabled:
            return
            
        self.histograms[metric_name].append(value)
        
        # Also record as time series
        timestamp = time.time()
        point = MetricPoint(timestamp, value, labels or {})
        self.metrics[metric_name].append(point)
        
    def record_model_inference(self, model_id: str, latency_ms: float, success: bool = True):
        """
        Record model inference metrics.
        
        Args:
            model_id: Model identifier
            latency_ms: Inference latency in milliseconds
            success: Whether inference was successful
        """
        labels = {"model_id": model_id}
        
        self.record_histogram("model.inference_latency_ms", latency_ms, labels)
        self.record_counter("model.inference_total", 1, labels)
        
        if success:
            self.record_counter("model.inference_success", 1, labels)
        else:
            self.record_counter("model.inference_error", 1, labels)
            
    def record_agent_task(self, agent_id: str, task_type: str, duration_s: float, success: bool = True):
        """
        Record agent task metrics.
        
        Args:
            agent_id: Agent identifier
            task_type: Type of task
            duration_s: Task duration in seconds
            success: Whether task was successful
        """
        labels = {"agent_id": agent_id, "task_type": task_type}
        
        self.record_histogram("agent.task_duration_s", duration_s, labels)
        self.record_counter("agent.task_total", 1, labels)
        
        if success:
            self.record_counter("agent.task_success", 1, labels)
        else:
            self.record_counter("agent.task_error", 1, labels)
            
    def record_api_request(self, endpoint: str, method: str, status_code: int, latency_ms: float):
        """
        Record API request metrics.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            latency_ms: Request latency in milliseconds
        """
        labels = {"endpoint": endpoint, "method": method, "status": str(status_code)}
        
        self.record_histogram("api.request_latency_ms", latency_ms, labels)
        self.record_counter("api.request_total", 1, labels)
        
        if 200 <= status_code < 300:
            self.record_counter("api.request_success", 1, labels)
        else:
            self.record_counter("api.request_error", 1, labels)
            
    def get_current_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return self._system_metrics
        
    def get_metric_summary(self, metric_name: str, 
                          time_range_s: int = 300) -> Dict[str, float]:
        """
        Get summary statistics for a metric over time range.
        
        Args:
            metric_name: Name of the metric
            time_range_s: Time range in seconds (default 5 minutes)
            
        Returns:
            Dictionary with summary statistics
        """
        if metric_name not in self.metrics:
            return {}
            
        current_time = time.time()
        cutoff_time = current_time - time_range_s
        
        # Filter points within time range
        points = [
            point for point in self.metrics[metric_name]
            if point.timestamp >= cutoff_time
        ]
        
        if not points:
            return {}
            
        values = [point.value for point in points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "latest": values[-1] if values else 0,
            "p50": self._percentile(values, 0.5),
            "p90": self._percentile(values, 0.9),
            "p95": self._percentile(values, 0.95),
            "p99": self._percentile(values, 0.99)
        }
        
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0
            
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        result = {
            "system": {
                "cpu_percent": self._system_metrics.cpu_percent,
                "memory_percent": self._system_metrics.memory_percent,
                "memory_used_gb": self._system_metrics.memory_used_gb,
                "memory_total_gb": self._system_metrics.memory_total_gb,
                "disk_percent": self._system_metrics.disk_percent,
                "disk_used_gb": self._system_metrics.disk_used_gb,
                "disk_total_gb": self._system_metrics.disk_total_gb,
                "network_bytes_sent": self._system_metrics.network_bytes_sent,
                "network_bytes_recv": self._system_metrics.network_bytes_recv
            },
            "counters": dict(self.counters),
            "gauges": {},
            "histograms": {}
        }
        
        # Add GPU metrics if available
        if self._system_metrics.gpu_percent is not None:
            result["system"]["gpu_percent"] = self._system_metrics.gpu_percent
            result["system"]["gpu_memory_used"] = self._system_metrics.gpu_memory_used
            result["system"]["gpu_memory_total"] = self._system_metrics.gpu_memory_total
            
        # Add latest gauge values
        for metric_name, points in self.metrics.items():
            if points:
                result["gauges"][metric_name] = points[-1].value
                
        # Add histogram summaries
        for metric_name, values in self.histograms.items():
            if values:
                result["histograms"][metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values)
                }
                
        return result
        
    def get_current(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return {
            "system": {
                "cpu_percent": self._system_metrics.cpu_percent,
                "memory_percent": self._system_metrics.memory_percent,
                "disk_percent": self._system_metrics.disk_percent,
                "gpu_percent": self._system_metrics.gpu_percent
            },
            "metrics_count": len(self.metrics),
            "counters_count": len(self.counters)
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on metrics system."""
        return {
            "status": "healthy" if self.enabled else "disabled",
            "monitoring_enabled": self.enabled,
            "system_metrics_available": self._system_metrics is not None,
            "metrics_collected": len(self.metrics),
            "counters_active": len(self.counters)
        }
        
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # System metrics
        lines.append(f"# HELP system_cpu_percent CPU usage percentage")
        lines.append(f"# TYPE system_cpu_percent gauge")
        lines.append(f"system_cpu_percent {self._system_metrics.cpu_percent}")
        
        lines.append(f"# HELP system_memory_percent Memory usage percentage")
        lines.append(f"# TYPE system_memory_percent gauge")
        lines.append(f"system_memory_percent {self._system_metrics.memory_percent}")
        
        # Counters
        for name, value in self.counters.items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"# HELP {safe_name} Counter metric")
            lines.append(f"# TYPE {safe_name} counter")
            lines.append(f"{safe_name} {value}")
            
        return "\n".join(lines)
        
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.histograms.clear()
        logger.info("Metrics cleared")
        
    def stop(self):
        """Stop metrics collection."""
        if not self.enabled:
            return
            
        self._shutdown = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
            
        logger.info("Metrics collector stopped")