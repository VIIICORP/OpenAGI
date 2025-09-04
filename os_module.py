"""
Operating System Module for OpenAGI
Simulates core OS functions for educational purposes
"""

import os
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, List, Any
from core import BaseModule, SystemStatus, Priority


class ProcessInfo:
    """Information about a system process"""
    def __init__(self, pid: int, name: str, cpu_percent: float, memory_percent: float):
        self.pid = pid
        self.name = name
        self.cpu_percent = cpu_percent
        self.memory_percent = memory_percent
        self.created_at = datetime.now()


class OperatingSystemModule(BaseModule):
    """Simulates core operating system functions"""
    
    def __init__(self):
        super().__init__("OperatingSystem")
        self.monitored_processes: Dict[int, ProcessInfo] = {}
        self.system_metrics = {}
        self.resource_limits = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0
        }
        self.alerts: List[Dict[str, Any]] = []
        
    def initialize(self) -> bool:
        """Initialize the OS module"""
        try:
            self.logger.info("Initializing Operating System module...")
            self._update_system_metrics()
            self.status = SystemStatus.RUNNING
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize OS module: {e}")
            self.status = SystemStatus.ERROR
            return False
            
    def start(self) -> bool:
        """Start the OS monitoring"""
        try:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            self.logger.info("Operating System monitoring started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start OS monitoring: {e}")
            return False
            
    def stop(self) -> bool:
        """Stop the OS monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.status = SystemStatus.SHUTDOWN
        self.logger.info("Operating System monitoring stopped")
        return True
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                self._update_system_metrics()
                self._monitor_processes()
                self._check_resource_limits()
                self.heartbeat()
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
                
    def _update_system_metrics(self):
        """Update system resource metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_info = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            except:
                network_info = {}
            
            self.system_metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': network_info
            }
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {e}")
            
    def _monitor_processes(self):
        """Monitor running processes"""
        try:
            current_processes = {}
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    current_processes[info['pid']] = ProcessInfo(
                        info['pid'],
                        info['name'],
                        info['cpu_percent'] or 0,
                        info['memory_percent'] or 0
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            self.monitored_processes = current_processes
        except Exception as e:
            self.logger.error(f"Error monitoring processes: {e}")
            
    def _check_resource_limits(self):
        """Check if resource usage exceeds limits"""
        if not self.system_metrics:
            return
            
        alerts = []
        
        # Check CPU usage
        cpu_percent = self.system_metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.resource_limits['cpu_threshold']:
            alerts.append({
                'type': 'resource_limit',
                'severity': Priority.HIGH,
                'message': f"High CPU usage: {cpu_percent:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
            
        # Check memory usage
        memory_percent = self.system_metrics.get('memory', {}).get('percent', 0)
        if memory_percent > self.resource_limits['memory_threshold']:
            alerts.append({
                'type': 'resource_limit',
                'severity': Priority.HIGH,
                'message': f"High memory usage: {memory_percent:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
            
        # Check disk usage
        disk_percent = self.system_metrics.get('disk', {}).get('percent', 0)
        if disk_percent > self.resource_limits['disk_threshold']:
            alerts.append({
                'type': 'resource_limit',
                'severity': Priority.CRITICAL,
                'message': f"High disk usage: {disk_percent:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
            
        for alert in alerts:
            self.alerts.append(alert)
            self.logger.warning(f"Resource Alert: {alert['message']}")
            
        # Keep only last 100 alerts
        self.alerts = self.alerts[-100:]
        
    def get_status(self) -> Dict[str, Any]:
        """Get OS module status"""
        return {
            'module': self.name,
            'status': self.status.value,
            'system_metrics': self.system_metrics,
            'process_count': len(self.monitored_processes),
            'recent_alerts': self.alerts[-10:],  # Last 10 alerts
            'resource_limits': self.resource_limits,
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }
        
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[Dict[str, Any]]:
        """Get top processes by CPU or memory usage"""
        processes = list(self.monitored_processes.values())
        
        if sort_by == 'cpu':
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
            
        return [
            {
                'pid': p.pid,
                'name': p.name,
                'cpu_percent': p.cpu_percent,
                'memory_percent': p.memory_percent
            }
            for p in processes[:limit]
        ]
        
    def set_resource_limit(self, resource: str, threshold: float):
        """Set resource usage threshold"""
        if resource in self.resource_limits:
            self.resource_limits[resource] = threshold
            self.logger.info(f"Updated {resource} threshold to {threshold}%")
        else:
            self.logger.warning(f"Unknown resource type: {resource}")
            
    def kill_process(self, pid: int) -> bool:
        """Terminate a process (simulation)"""
        try:
            if pid in self.monitored_processes:
                process_name = self.monitored_processes[pid].name
                self.logger.info(f"Simulating termination of process {pid} ({process_name})")
                # In a real implementation, this would actually terminate the process
                # For simulation, we just log it
                return True
            else:
                self.logger.warning(f"Process {pid} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error terminating process {pid}: {e}")
            return False