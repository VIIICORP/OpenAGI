"""
Comprehensive monitoring system for OpenAGI platform.

Features:
- Real-time metrics collection
- Performance monitoring
- Resource usage tracking
- Alerting system
- Historical data analysis
- Anomaly detection
- Custom dashboards
"""

import asyncio
import time
import psutil
import threading
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram, Gauge, start_http_server
from openagi.core.config import OpenAGIConfig
from openagi.core.logger import get_openagi_logger


@dataclass
class MetricValue:
    """Represents a metric value with timestamp."""
    timestamp: datetime
    value: float
    labels: Dict[str, str]


class MetricsCollector:
    """Collects various system and application metrics."""
    
    def __init__(self, config: OpenAGIConfig):
        self.config = config
        self.logger = get_openagi_logger("metrics_collector")
        
        # Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Internal metrics storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.custom_metrics: Dict[str, Callable] = {}
        
    def setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics."""
        # System metrics
        self.cpu_usage = Gauge('openagi_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('openagi_memory_usage_percent', 'Memory usage percentage')
        self.disk_usage = Gauge('openagi_disk_usage_percent', 'Disk usage percentage')
        
        # Application metrics
        self.request_count = Counter('openagi_requests_total', 'Total requests', ['method', 'endpoint'])
        self.request_duration = Histogram('openagi_request_duration_seconds', 'Request duration')
        self.error_count = Counter('openagi_errors_total', 'Total errors', ['type', 'component'])
        
        # Debugging metrics
        self.debug_events = Counter('openagi_debug_events_total', 'Debug events', ['type', 'severity'])
        self.healing_attempts = Counter('openagi_healing_attempts_total', 'Healing attempts', ['type', 'success'])
        
        # AI metrics
        self.model_inference_time = Histogram('openagi_model_inference_seconds', 'Model inference time')
        self.model_memory_usage = Gauge('openagi_model_memory_bytes', 'Model memory usage')
    
    async def collect_system_metrics(self) -> Dict[str, MetricValue]:
        """Collect system-level metrics."""
        metrics = {}
        now = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        metrics['cpu_usage'] = MetricValue(now, cpu_percent, {})
        self.cpu_usage.set(cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics['memory_usage'] = MetricValue(now, memory.percent, {})
        self.memory_usage.set(memory.percent)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics['disk_usage'] = MetricValue(now, disk.percent, {})
        self.disk_usage.set(disk.percent)
        
        # Network metrics
        network = psutil.net_io_counters()
        metrics['network_bytes_sent'] = MetricValue(now, network.bytes_sent, {})
        metrics['network_bytes_recv'] = MetricValue(now, network.bytes_recv, {})
        
        # Process metrics
        process = psutil.Process()
        metrics['process_memory'] = MetricValue(now, process.memory_info().rss, {})
        metrics['process_cpu'] = MetricValue(now, process.cpu_percent(), {})
        metrics['process_threads'] = MetricValue(now, process.num_threads(), {})
        
        return metrics
    
    async def collect_application_metrics(self) -> Dict[str, MetricValue]:
        """Collect application-specific metrics."""
        metrics = {}
        now = datetime.now()
        
        # Thread metrics
        thread_count = threading.active_count()
        metrics['active_threads'] = MetricValue(now, thread_count, {})
        
        # Asyncio metrics
        try:
            loop = asyncio.get_running_loop()
            task_count = len([t for t in asyncio.all_tasks(loop) if not t.done()])
            metrics['active_async_tasks'] = MetricValue(now, task_count, {})
        except RuntimeError:
            pass
        
        return metrics
    
    def record_request(self, method: str, endpoint: str, duration: float) -> None:
        """Record HTTP request metrics."""
        self.request_count.labels(method=method, endpoint=endpoint).inc()
        self.request_duration.observe(duration)
    
    def record_error(self, error_type: str, component: str) -> None:
        """Record error metrics."""
        self.error_count.labels(type=error_type, component=component).inc()
    
    def record_debug_event(self, event_type: str, severity: str) -> None:
        """Record debug event metrics."""
        self.debug_events.labels(type=event_type, severity=severity).inc()
    
    def record_healing_attempt(self, healing_type: str, success: bool) -> None:
        """Record healing attempt metrics."""
        self.healing_attempts.labels(type=healing_type, success=str(success)).inc()


class AlertingSystem:
    """Intelligent alerting system with threshold monitoring."""
    
    def __init__(self, config: OpenAGIConfig):
        self.config = config
        self.logger = get_openagi_logger("alerting")
        
        # Alert rules
        self.alert_rules: Dict[str, Dict] = {
            'high_cpu': {
                'metric': 'cpu_usage',
                'threshold': 80.0,
                'duration': 300,  # 5 minutes
                'severity': 'warning'
            },
            'high_memory': {
                'metric': 'memory_usage',
                'threshold': 85.0,
                'duration': 180,  # 3 minutes
                'severity': 'critical'
            },
            'disk_full': {
                'metric': 'disk_usage',
                'threshold': 95.0,
                'duration': 60,  # 1 minute
                'severity': 'critical'
            },
            'error_rate_high': {
                'metric': 'error_rate',
                'threshold': 10.0,  # errors per minute
                'duration': 120,  # 2 minutes
                'severity': 'warning'
            }
        }
        
        # Alert state
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict] = []
        
    async def check_alerts(self, metrics: Dict[str, MetricValue]) -> List[Dict]:
        """Check metrics against alert rules."""
        alerts = []
        now = datetime.now()
        
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule['metric']
            
            if metric_name in metrics:
                metric_value = metrics[metric_name]
                threshold = rule['threshold']
                
                if metric_value.value > threshold:
                    # Check if alert is already active
                    if rule_name not in self.active_alerts:
                        self.active_alerts[rule_name] = now
                    
                    # Check if duration threshold is met
                    alert_duration = (now - self.active_alerts[rule_name]).total_seconds()
                    if alert_duration >= rule['duration']:
                        alert = {
                            'rule': rule_name,
                            'metric': metric_name,
                            'value': metric_value.value,
                            'threshold': threshold,
                            'severity': rule['severity'],
                            'timestamp': now,
                            'duration': alert_duration
                        }
                        alerts.append(alert)
                        
                        # Log alert
                        self.logger.warning(
                            f"Alert triggered: {rule_name}",
                            metric=metric_name,
                            value=metric_value.value,
                            threshold=threshold,
                            severity=rule['severity']
                        )
                else:
                    # Clear alert if metric is below threshold
                    if rule_name in self.active_alerts:
                        del self.active_alerts[rule_name]
        
        return alerts


class PerformanceAnalyzer:
    """Analyzes performance patterns and identifies bottlenecks."""
    
    def __init__(self, config: OpenAGIConfig):
        self.config = config
        self.logger = get_openagi_logger("performance_analyzer")
        
        # Performance baselines
        self.baselines: Dict[str, float] = {}
        self.trends: Dict[str, List[float]] = defaultdict(list)
        
    async def analyze_performance(self, metrics: Dict[str, MetricValue]) -> Dict[str, Any]:
        """Analyze current performance against baselines."""
        analysis = {
            'timestamp': datetime.now(),
            'bottlenecks': [],
            'trends': {},
            'recommendations': []
        }
        
        for metric_name, metric_value in metrics.items():
            # Update trends
            self.trends[metric_name].append(metric_value.value)
            if len(self.trends[metric_name]) > 100:
                self.trends[metric_name] = self.trends[metric_name][-100:]
            
            # Calculate baseline if not exists
            if metric_name not in self.baselines and len(self.trends[metric_name]) >= 10:
                self.baselines[metric_name] = sum(self.trends[metric_name][:10]) / 10
            
            # Analyze against baseline
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]
                current = metric_value.value
                deviation = (current - baseline) / baseline if baseline > 0 else 0
                
                # Detect significant deviations
                if abs(deviation) > 0.5:  # 50% deviation
                    bottleneck = {
                        'metric': metric_name,
                        'current': current,
                        'baseline': baseline,
                        'deviation': deviation,
                        'severity': 'high' if abs(deviation) > 1.0 else 'medium'
                    }
                    analysis['bottlenecks'].append(bottleneck)
                
                # Calculate trend
                if len(self.trends[metric_name]) >= 5:
                    recent_trend = sum(self.trends[metric_name][-5:]) / 5
                    older_trend = sum(self.trends[metric_name][-10:-5]) / 5 if len(self.trends[metric_name]) >= 10 else recent_trend
                    trend_direction = 'increasing' if recent_trend > older_trend else 'decreasing'
                    
                    analysis['trends'][metric_name] = {
                        'direction': trend_direction,
                        'magnitude': abs(recent_trend - older_trend)
                    }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        for bottleneck in analysis.get('bottlenecks', []):
            metric = bottleneck['metric']
            
            if metric == 'cpu_usage' and bottleneck['deviation'] > 0:
                recommendations.append("Consider optimizing CPU-intensive operations")
                recommendations.append("Review algorithm complexity and implementation")
            
            elif metric == 'memory_usage' and bottleneck['deviation'] > 0:
                recommendations.append("Investigate memory leaks or excessive memory usage")
                recommendations.append("Consider implementing memory pooling or caching strategies")
            
            elif metric == 'disk_usage' and bottleneck['deviation'] > 0:
                recommendations.append("Clean up temporary files and logs")
                recommendations.append("Consider implementing data archiving strategies")
        
        return recommendations


class MonitoringSystem:
    """Main monitoring system that orchestrates all monitoring components."""
    
    def __init__(self, config: OpenAGIConfig):
        self.config = config
        self.logger = get_openagi_logger("monitoring_system")
        
        # Components
        self.metrics_collector = MetricsCollector(config)
        self.alerting_system = AlertingSystem(config)
        self.performance_analyzer = PerformanceAnalyzer(config)
        
        # State
        self._running = False
        self.monitoring_data: Dict[str, Any] = {}
        
        # Prometheus server
        self.prometheus_server = None
    
    async def initialize(self) -> None:
        """Initialize the monitoring system."""
        self.logger.info("Initializing monitoring system")
        
        # Start Prometheus metrics server if enabled
        if self.config.monitoring.enable_prometheus:
            try:
                start_http_server(self.config.monitoring.metrics_port)
                self.logger.info(f"Prometheus metrics server started on port {self.config.monitoring.metrics_port}")
            except Exception as e:
                self.logger.error("Failed to start Prometheus server", error=str(e))
        
        self.logger.info("Monitoring system initialized")
    
    async def start(self) -> None:
        """Start the monitoring system."""
        if self._running:
            return
        
        self.logger.info("Starting monitoring system")
        self._running = True
        
        # Start monitoring loop
        while self._running:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitoring cycle error", error=str(e))
                await asyncio.sleep(30)  # Back off on errors
    
    async def shutdown(self) -> None:
        """Shutdown the monitoring system."""
        self.logger.info("Shutting down monitoring system")
        self._running = False
        self.logger.info("Monitoring system shutdown complete")
    
    async def _monitoring_cycle(self) -> None:
        """Main monitoring cycle."""
        # Collect metrics
        system_metrics = await self.metrics_collector.collect_system_metrics()
        app_metrics = await self.metrics_collector.collect_application_metrics()
        
        all_metrics = {**system_metrics, **app_metrics}
        
        # Store metrics for history
        for metric_name, metric_value in all_metrics.items():
            self.metrics_collector.metrics_history[metric_name].append(metric_value)
        
        # Check alerts
        alerts = await self.alerting_system.check_alerts(all_metrics)
        
        # Analyze performance
        performance_analysis = await self.performance_analyzer.analyze_performance(all_metrics)
        
        # Update monitoring data
        self.monitoring_data.update({
            'timestamp': datetime.now(),
            'metrics': all_metrics,
            'alerts': alerts,
            'performance_analysis': performance_analysis
        })
        
        # Log significant events
        if alerts:
            self.logger.warning(f"Active alerts: {len(alerts)}")
        
        if performance_analysis.get('bottlenecks'):
            self.logger.info(f"Performance bottlenecks detected: {len(performance_analysis['bottlenecks'])}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of monitoring system."""
        return {
            "healthy": self._running,
            "prometheus_enabled": self.config.monitoring.enable_prometheus,
            "metrics_collected": len(self.metrics_collector.metrics_history),
            "active_alerts": len(self.alerting_system.active_alerts),
            "components": {
                "metrics_collector": True,
                "alerting_system": True,
                "performance_analyzer": True
            }
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        summary = {}
        
        for metric_name, history in self.metrics_collector.metrics_history.items():
            if history:
                latest = history[-1]
                values = [m.value for m in history]
                
                summary[metric_name] = {
                    'current': latest.value,
                    'timestamp': latest.timestamp.isoformat(),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return summary
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get a summary of alerts."""
        return {
            'active_alerts': len(self.alerting_system.active_alerts),
            'alert_rules': list(self.alerting_system.alert_rules.keys()),
            'recent_alerts': self.alerting_system.alert_history[-10:] if self.alerting_system.alert_history else []
        }