"""
Health Monitoring Module

This module provides comprehensive health monitoring capabilities for the OpenAGI platform,
including system resource monitoring, agent health tracking, and performance metrics.
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json

from .config import ConfigManager


@dataclass
class HealthMetrics:
    """Health metrics for system components."""
    timestamp: float = field(default_factory=time.time)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, int] = field(default_factory=dict)
    process_count: int = 0
    uptime: float = 0.0
    temperature: Optional[float] = None
    gpu_usage: Optional[float] = None
    gpu_memory: Optional[float] = None


@dataclass
class AgentHealth:
    """Health information for an AI agent."""
    agent_id: str
    status: str = "healthy"
    last_heartbeat: float = field(default_factory=time.time)
    response_time: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    task_queue_size: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """
    Comprehensive health monitoring system for the OpenAGI platform.
    
    Monitors system resources, agent health, performance metrics, and provides
    real-time health status information for the self-healing system.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the health monitoring system."""
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self._running = False
        self.start_time = time.time()
        
        # Health data
        self._system_metrics: List[HealthMetrics] = []
        self._agent_health: Dict[str, AgentHealth] = {}
        self._alerts: List[Dict[str, Any]] = []
        
        # Thresholds
        self.cpu_threshold = self.config_manager.get("monitoring.cpu_threshold", 80.0)
        self.memory_threshold = self.config_manager.get("monitoring.memory_threshold", 85.0)
        self.disk_threshold = self.config_manager.get("monitoring.disk_threshold", 90.0)
        self.agent_timeout = self.config_manager.get("monitoring.agent_timeout", 60.0)
        
        # Metrics retention
        self.max_metrics_history = self.config_manager.get("monitoring.max_history", 1000)
        
        self.logger.info("Health monitoring system initialized")
    
    async def start(self) -> None:
        """Start the health monitoring system."""
        if self._running:
            return
        
        self._running = True
        self.start_time = time.time()
        
        # Start monitoring tasks
        asyncio.create_task(self._system_monitor())
        asyncio.create_task(self._agent_monitor())
        asyncio.create_task(self._performance_monitor())
        
        self.logger.info("Health monitoring system started")
    
    async def stop(self) -> None:
        """Stop the health monitoring system."""
        self._running = False
        self.logger.info("Health monitoring system stopped")
    
    async def register_agent(self, agent_id: str, agent_info: Any) -> None:
        """Register an agent for health monitoring."""
        agent_health = AgentHealth(agent_id=agent_id)
        self._agent_health[agent_id] = agent_health
        self.logger.info(f"Registered agent for health monitoring: {agent_id}")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from health monitoring."""
        if agent_id in self._agent_health:
            del self._agent_health[agent_id]
            self.logger.info(f"Unregistered agent from health monitoring: {agent_id}")
    
    async def update_agent_heartbeat(self, agent_id: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        """Update agent heartbeat and metrics."""
        if agent_id in self._agent_health:
            agent = self._agent_health[agent_id]
            agent.last_heartbeat = time.time()
            agent.status = "healthy"
            
            if metrics:
                agent.metrics.update(metrics)
                agent.response_time = metrics.get("response_time", agent.response_time)
                agent.memory_usage = metrics.get("memory_usage", agent.memory_usage)
                agent.cpu_usage = metrics.get("cpu_usage", agent.cpu_usage)
                agent.task_queue_size = metrics.get("task_queue_size", agent.task_queue_size)
    
    async def report_agent_error(self, agent_id: str, error: str) -> None:
        """Report an error for an agent."""
        if agent_id in self._agent_health:
            agent = self._agent_health[agent_id]
            agent.error_count += 1
            
            # Update success rate
            total_requests = agent.error_count + max(1, agent.metrics.get("success_count", 0))
            agent.success_rate = (total_requests - agent.error_count) / total_requests * 100
            
            self.logger.warning(f"Error reported for agent {agent_id}: {error}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        current_metrics = await self._collect_system_metrics()
        
        # Agent health summary
        healthy_agents = sum(1 for agent in self._agent_health.values() if agent.status == "healthy")
        total_agents = len(self._agent_health)
        
        # System health assessment
        system_health = "healthy"
        if (current_metrics.cpu_usage > self.cpu_threshold or 
            current_metrics.memory_usage > self.memory_threshold or 
            current_metrics.disk_usage > self.disk_threshold):
            system_health = "degraded"
        
        # Recent alerts
        recent_alerts = self._alerts[-10:] if self._alerts else []
        
        return {
            "timestamp": time.time(),
            "system_health": system_health,
            "uptime": time.time() - self.start_time,
            "cpu_usage": current_metrics.cpu_usage,
            "memory_usage": current_metrics.memory_usage,
            "disk_usage": current_metrics.disk_usage,
            "network_io": current_metrics.network_io,
            "process_count": current_metrics.process_count,
            "temperature": current_metrics.temperature,
            "gpu_usage": current_metrics.gpu_usage,
            "gpu_memory": current_metrics.gpu_memory,
            "agents": {
                "total": total_agents,
                "healthy": healthy_agents,
                "unhealthy": total_agents - healthy_agents,
                "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 100
            },
            "alerts": recent_alerts,
            "metrics_history_size": len(self._system_metrics)
        }
    
    async def get_agent_health(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get health information for a specific agent."""
        if agent_id not in self._agent_health:
            return None
        
        agent = self._agent_health[agent_id]
        return {
            "agent_id": agent.agent_id,
            "status": agent.status,
            "last_heartbeat": agent.last_heartbeat,
            "heartbeat_age": time.time() - agent.last_heartbeat,
            "response_time": agent.response_time,
            "error_count": agent.error_count,
            "success_rate": agent.success_rate,
            "memory_usage": agent.memory_usage,
            "cpu_usage": agent.cpu_usage,
            "task_queue_size": agent.task_queue_size,
            "metrics": agent.metrics
        }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources and return status."""
        metrics = await self._collect_system_metrics()
        
        issues = []
        if metrics.cpu_usage > self.cpu_threshold:
            issues.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > self.memory_threshold:
            issues.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        if metrics.disk_usage > self.disk_threshold:
            issues.append(f"High disk usage: {metrics.disk_usage:.1f}%")
        
        return {
            "status": "healthy" if not issues else "degraded",
            "issues": issues,
            "metrics": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "disk_usage": metrics.disk_usage,
                "process_count": metrics.process_count
            }
        }
    
    async def _system_monitor(self) -> None:
        """Monitor system resources continuously."""
        while self._running:
            try:
                metrics = await self._collect_system_metrics()
                self._system_metrics.append(metrics)
                
                # Trim history
                if len(self._system_metrics) > self.max_metrics_history:
                    self._system_metrics = self._system_metrics[-self.max_metrics_history:]
                
                # Check for alerts
                await self._check_system_alerts(metrics)
                
                await asyncio.sleep(5)  # Collect metrics every 5 seconds
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _agent_monitor(self) -> None:
        """Monitor agent health continuously."""
        while self._running:
            try:
                current_time = time.time()
                
                for agent_id, agent in self._agent_health.items():
                    heartbeat_age = current_time - agent.last_heartbeat
                    
                    # Check for timeout
                    if heartbeat_age > self.agent_timeout:
                        if agent.status != "timeout":
                            agent.status = "timeout"
                            await self._create_alert("agent_timeout", {
                                "agent_id": agent_id,
                                "heartbeat_age": heartbeat_age
                            })
                    
                    # Check for performance issues
                    if agent.response_time > 5.0:  # 5 second threshold
                        await self._create_alert("agent_slow_response", {
                            "agent_id": agent_id,
                            "response_time": agent.response_time
                        })
                    
                    if agent.success_rate < 90.0:  # 90% success rate threshold
                        await self._create_alert("agent_low_success_rate", {
                            "agent_id": agent_id,
                            "success_rate": agent.success_rate
                        })
                
                await asyncio.sleep(10)  # Check agents every 10 seconds
            except Exception as e:
                self.logger.error(f"Agent monitoring error: {e}")
                await asyncio.sleep(15)
    
    async def _performance_monitor(self) -> None:
        """Monitor performance metrics and trends."""
        while self._running:
            try:
                # Analyze performance trends
                if len(self._system_metrics) >= 10:
                    await self._analyze_performance_trends()
                
                await asyncio.sleep(60)  # Analyze trends every minute
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _collect_system_metrics(self) -> HealthMetrics:
        """Collect current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature sensor
                    for name, entries in temps.items():
                        if entries:
                            temperature = entries[0].current
                            break
            except (AttributeError, OSError):
                pass  # Temperature sensors not available
            
            # GPU metrics (if available)
            gpu_usage = None
            gpu_memory = None
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # First GPU
                    gpu_usage = gpu.load * 100
                    gpu_memory = gpu.memoryUtil * 100
            except (ImportError, Exception):
                pass  # GPU monitoring not available
            
            return HealthMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                network_io=network_io,
                process_count=process_count,
                uptime=time.time() - self.start_time,
                temperature=temperature,
                gpu_usage=gpu_usage,
                gpu_memory=gpu_memory
            )
        
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return HealthMetrics()  # Return empty metrics on error
    
    async def _check_system_alerts(self, metrics: HealthMetrics) -> None:
        """Check system metrics for alert conditions."""
        if metrics.cpu_usage > self.cpu_threshold:
            await self._create_alert("high_cpu_usage", {
                "cpu_usage": metrics.cpu_usage,
                "threshold": self.cpu_threshold
            })
        
        if metrics.memory_usage > self.memory_threshold:
            await self._create_alert("high_memory_usage", {
                "memory_usage": metrics.memory_usage,
                "threshold": self.memory_threshold
            })
        
        if metrics.disk_usage > self.disk_threshold:
            await self._create_alert("high_disk_usage", {
                "disk_usage": metrics.disk_usage,
                "threshold": self.disk_threshold
            })
        
        if metrics.temperature and metrics.temperature > 80.0:  # 80°C threshold
            await self._create_alert("high_temperature", {
                "temperature": metrics.temperature,
                "threshold": 80.0
            })
        
        if metrics.gpu_usage and metrics.gpu_usage > 95.0:  # 95% GPU usage threshold
            await self._create_alert("high_gpu_usage", {
                "gpu_usage": metrics.gpu_usage,
                "threshold": 95.0
            })
    
    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends for predictive alerting."""
        if len(self._system_metrics) < 10:
            return
        
        recent_metrics = self._system_metrics[-10:]
        
        # Calculate trends
        cpu_trend = self._calculate_trend([m.cpu_usage for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_usage for m in recent_metrics])
        disk_trend = self._calculate_trend([m.disk_usage for m in recent_metrics])
        
        # Predictive alerts
        if cpu_trend > 2.0:  # CPU usage increasing by more than 2% per measurement
            await self._create_alert("cpu_usage_trending_up", {
                "trend": cpu_trend,
                "current_usage": recent_metrics[-1].cpu_usage
            })
        
        if memory_trend > 1.0:  # Memory usage increasing by more than 1% per measurement
            await self._create_alert("memory_usage_trending_up", {
                "trend": memory_trend,
                "current_usage": recent_metrics[-1].memory_usage
            })
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate the trend (slope) of a series of values."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * v for i, v in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        # Linear regression slope
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    async def _create_alert(self, alert_type: str, context: Dict[str, Any]) -> None:
        """Create an alert."""
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "context": context,
            "id": f"alert_{int(time.time() * 1000)}"
        }
        
        self._alerts.append(alert)
        
        # Trim alerts history
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        
        self.logger.warning(f"Alert created: {alert_type} - {context}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "uptime": time.time() - self.start_time,
            "metrics_collected": len(self._system_metrics),
            "agents_monitored": len(self._agent_health),
            "alerts_generated": len(self._alerts),
            "monitoring_status": "running" if self._running else "stopped",
            "thresholds": {
                "cpu": self.cpu_threshold,
                "memory": self.memory_threshold,
                "disk": self.disk_threshold,
                "agent_timeout": self.agent_timeout
            }
        }