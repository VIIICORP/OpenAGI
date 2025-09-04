"""
Health and Upgrade Board Module for OpenAGI
Manages system health monitoring and upgrade processes
"""

import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from core import BaseModule, SystemStatus, Priority


class HealthStatus(Enum):
    """System health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILURE = "failure"


class UpgradeStatus(Enum):
    """Upgrade process status"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class HealthMetric:
    """Health monitoring metric"""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    status: HealthStatus


@dataclass
class UpgradePackage:
    """Upgrade package information"""
    id: str
    name: str
    version: str
    description: str
    size_mb: float
    priority: Priority
    dependencies: List[str]
    created_at: datetime
    status: UpgradeStatus
    progress: float = 0.0
    error_message: Optional[str] = None


class HealthUpgradeBoardModule(BaseModule):
    """Health monitoring and upgrade management system"""
    
    def __init__(self):
        super().__init__("HealthUpgradeBoard")
        self.health_metrics: Dict[str, HealthMetric] = {}
        self.upgrade_queue: List[str] = []
        self.upgrade_packages: Dict[str, UpgradePackage] = {}
        self.system_health_score = 100.0
        self.maintenance_window = None
        self.auto_upgrade_enabled = True
        self.health_history: List[Dict[str, Any]] = []
        
        # Initialize health monitoring metrics
        self._initialize_health_metrics()
        
    def initialize(self) -> bool:
        """Initialize the health and upgrade board"""
        try:
            self.logger.info("Initializing Health and Upgrade Board...")
            self._load_upgrade_catalog()
            self.status = SystemStatus.RUNNING
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Health Upgrade Board: {e}")
            self.status = SystemStatus.ERROR
            return False
            
    def start(self) -> bool:
        """Start health monitoring and upgrade services"""
        try:
            self._running = True
            self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._thread.start()
            
            self.logger.info("Health and Upgrade Board services started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Health Upgrade Board: {e}")
            return False
            
    def stop(self) -> bool:
        """Stop health monitoring and upgrade services"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.status = SystemStatus.SHUTDOWN
        self.logger.info("Health and Upgrade Board services stopped")
        return True
        
    def _initialize_health_metrics(self):
        """Initialize health monitoring metrics"""
        metrics = [
            ("cpu_usage", 0.0, "%", 80.0, 95.0),
            ("memory_usage", 0.0, "%", 85.0, 95.0),
            ("disk_usage", 0.0, "%", 80.0, 90.0),
            ("network_latency", 0.0, "ms", 100.0, 500.0),
            ("error_rate", 0.0, "%", 5.0, 10.0),
            ("response_time", 0.0, "ms", 1000.0, 5000.0),
            ("uptime", 100.0, "%", 99.0, 95.0),
            ("security_score", 100.0, "score", 80.0, 60.0)
        ]
        
        for name, value, unit, warning, critical in metrics:
            self.health_metrics[name] = HealthMetric(
                name=name,
                value=value,
                unit=unit,
                threshold_warning=warning,
                threshold_critical=critical,
                timestamp=datetime.now(),
                status=HealthStatus.GOOD
            )
            
    def _load_upgrade_catalog(self):
        """Load available upgrade packages"""
        # Simulate loading upgrade catalog
        sample_upgrades = [
            {
                'id': 'security-patch-001',
                'name': 'Security Update',
                'version': '1.2.3',
                'description': 'Critical security patches',
                'size_mb': 45.2,
                'priority': Priority.CRITICAL,
                'dependencies': []
            },
            {
                'id': 'system-update-002',
                'name': 'System Enhancement',
                'version': '2.1.0',
                'description': 'Performance improvements',
                'size_mb': 128.5,
                'priority': Priority.MEDIUM,
                'dependencies': ['security-patch-001']
            }
        ]
        
        for upgrade_data in sample_upgrades:
            package = UpgradePackage(
                id=upgrade_data['id'],
                name=upgrade_data['name'],
                version=upgrade_data['version'],
                description=upgrade_data['description'],
                size_mb=upgrade_data['size_mb'],
                priority=upgrade_data['priority'],
                dependencies=upgrade_data['dependencies'],
                created_at=datetime.now(),
                status=UpgradeStatus.PENDING
            )
            self.upgrade_packages[package.id] = package
            
        self.logger.info(f"Loaded {len(self.upgrade_packages)} upgrade packages")
        
    def _monitoring_loop(self):
        """Main health monitoring loop"""
        while self._running:
            try:
                self._update_health_metrics()
                self._calculate_health_score()
                self._check_upgrade_schedule()
                self._record_health_history()
                self.heartbeat()
                time.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
                
    def _update_health_metrics(self):
        """Update all health metrics"""
        import random
        import psutil
        
        try:
            # Update system metrics with real data where possible
            if 'cpu_usage' in self.health_metrics:
                self.health_metrics['cpu_usage'].value = psutil.cpu_percent()
                self.health_metrics['cpu_usage'].timestamp = datetime.now()
                
            if 'memory_usage' in self.health_metrics:
                self.health_metrics['memory_usage'].value = psutil.virtual_memory().percent
                self.health_metrics['memory_usage'].timestamp = datetime.now()
                
            if 'disk_usage' in self.health_metrics:
                self.health_metrics['disk_usage'].value = psutil.disk_usage('/').percent
                self.health_metrics['disk_usage'].timestamp = datetime.now()
                
            # Simulate other metrics
            self.health_metrics['network_latency'].value = random.uniform(10, 150)
            self.health_metrics['error_rate'].value = random.uniform(0, 3)
            self.health_metrics['response_time'].value = random.uniform(50, 800)
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - self.created_at).total_seconds()
            uptime_hours = uptime_seconds / 3600
            self.health_metrics['uptime'].value = min(100.0, (uptime_hours / (uptime_hours + 0.1)) * 100)
            
            # Update health status for each metric
            for metric in self.health_metrics.values():
                if metric.value >= metric.threshold_critical:
                    metric.status = HealthStatus.CRITICAL
                elif metric.value >= metric.threshold_warning:
                    metric.status = HealthStatus.WARNING
                else:
                    metric.status = HealthStatus.GOOD
                    
        except Exception as e:
            self.logger.error(f"Error updating health metrics: {e}")
            
    def _calculate_health_score(self):
        """Calculate overall system health score"""
        if not self.health_metrics:
            return
            
        total_score = 0
        metric_count = 0
        
        for metric in self.health_metrics.values():
            if metric.status == HealthStatus.GOOD:
                score = 100
            elif metric.status == HealthStatus.WARNING:
                score = 70
            elif metric.status == HealthStatus.CRITICAL:
                score = 30
            else:
                score = 0
                
            total_score += score
            metric_count += 1
            
        if metric_count > 0:
            self.system_health_score = total_score / metric_count
        else:
            self.system_health_score = 0
            
    def _check_upgrade_schedule(self):
        """Check if upgrades should be processed"""
        if not self.auto_upgrade_enabled:
            return
            
        # Process critical upgrades immediately
        for package_id, package in self.upgrade_packages.items():
            if (package.status == UpgradeStatus.PENDING and 
                package.priority == Priority.CRITICAL):
                self._schedule_upgrade(package_id)
                
        # Process other upgrades during maintenance window
        if self._is_maintenance_window():
            for package_id, package in self.upgrade_packages.items():
                if package.status == UpgradeStatus.PENDING:
                    self._schedule_upgrade(package_id)
                    break  # Process one at a time
                    
    def _is_maintenance_window(self) -> bool:
        """Check if current time is within maintenance window"""
        if not self.maintenance_window:
            return False
            
        current_time = datetime.now().time()
        start_time = self.maintenance_window.get('start')
        end_time = self.maintenance_window.get('end')
        
        if start_time and end_time:
            return start_time <= current_time <= end_time
        return False
        
    def _schedule_upgrade(self, package_id: str):
        """Schedule an upgrade for processing"""
        if package_id not in self.upgrade_queue:
            self.upgrade_queue.append(package_id)
            self.logger.info(f"Scheduled upgrade: {package_id}")
            
            # Start upgrade process in separate thread
            upgrade_thread = threading.Thread(
                target=self._process_upgrade, 
                args=(package_id,), 
                daemon=True
            )
            upgrade_thread.start()
            
    def _process_upgrade(self, package_id: str):
        """Process an upgrade package"""
        if package_id not in self.upgrade_packages:
            return
            
        package = self.upgrade_packages[package_id]
        
        try:
            self.logger.info(f"Starting upgrade: {package.name} v{package.version}")
            
            # Check dependencies
            for dep_id in package.dependencies:
                if (dep_id in self.upgrade_packages and 
                    self.upgrade_packages[dep_id].status != UpgradeStatus.COMPLETED):
                    package.status = UpgradeStatus.FAILED
                    package.error_message = f"Dependency {dep_id} not satisfied"
                    self.logger.error(f"Upgrade {package_id} failed: dependency not satisfied")
                    return
                    
            # Simulate upgrade process
            stages = [
                (UpgradeStatus.DOWNLOADING, 20),
                (UpgradeStatus.INSTALLING, 60),
                (UpgradeStatus.TESTING, 20)
            ]
            
            for status, duration in stages:
                package.status = status
                self.logger.info(f"Upgrade {package_id}: {status.value}")
                
                # Simulate progress
                for i in range(duration):
                    if not self._running:
                        return
                    package.progress = (i / duration) * 100
                    time.sleep(0.1)  # Simulate work
                    
            package.status = UpgradeStatus.COMPLETED
            package.progress = 100.0
            self.logger.info(f"Upgrade {package_id} completed successfully")
            
            # Remove from queue
            if package_id in self.upgrade_queue:
                self.upgrade_queue.remove(package_id)
                
        except Exception as e:
            package.status = UpgradeStatus.FAILED
            package.error_message = str(e)
            self.logger.error(f"Upgrade {package_id} failed: {e}")
            
            if package_id in self.upgrade_queue:
                self.upgrade_queue.remove(package_id)
                
    def _record_health_history(self):
        """Record health metrics to history"""
        health_snapshot = {
            'timestamp': datetime.now().isoformat(),
            'health_score': self.system_health_score,
            'metrics': {
                name: {
                    'value': metric.value,
                    'status': metric.status.value
                }
                for name, metric in self.health_metrics.items()
            }
        }
        
        self.health_history.append(health_snapshot)
        
        # Keep only last 100 records
        self.health_history = self.health_history[-100:]
        
    def add_upgrade_package(self, name: str, version: str, description: str, 
                           size_mb: float, priority: Priority = Priority.MEDIUM,
                           dependencies: List[str] = None) -> str:
        """Add a new upgrade package"""
        package_id = f"{name.lower().replace(' ', '-')}-{version}"
        
        package = UpgradePackage(
            id=package_id,
            name=name,
            version=version,
            description=description,
            size_mb=size_mb,
            priority=priority,
            dependencies=dependencies or [],
            created_at=datetime.now(),
            status=UpgradeStatus.PENDING
        )
        
        self.upgrade_packages[package_id] = package
        self.logger.info(f"Added upgrade package: {package_id}")
        return package_id
        
    def set_maintenance_window(self, start_hour: int, end_hour: int):
        """Set maintenance window (24-hour format)"""
        from datetime import time
        
        self.maintenance_window = {
            'start': time(start_hour, 0),
            'end': time(end_hour, 0)
        }
        self.logger.info(f"Set maintenance window: {start_hour:02d}:00 - {end_hour:02d}:00")
        
    def enable_auto_upgrade(self, enabled: bool):
        """Enable or disable automatic upgrades"""
        self.auto_upgrade_enabled = enabled
        self.logger.info(f"Auto-upgrade {'enabled' if enabled else 'disabled'}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get health and upgrade board status"""
        pending_upgrades = [p for p in self.upgrade_packages.values() 
                           if p.status == UpgradeStatus.PENDING]
        in_progress_upgrades = [p for p in self.upgrade_packages.values() 
                               if p.status in [UpgradeStatus.DOWNLOADING, UpgradeStatus.INSTALLING, UpgradeStatus.TESTING]]
        
        # Determine overall system health
        if self.system_health_score >= 90:
            overall_health = HealthStatus.EXCELLENT
        elif self.system_health_score >= 75:
            overall_health = HealthStatus.GOOD
        elif self.system_health_score >= 50:
            overall_health = HealthStatus.WARNING
        else:
            overall_health = HealthStatus.CRITICAL
            
        return {
            'module': self.name,
            'status': self.status.value,
            'system_health_score': self.system_health_score,
            'overall_health': overall_health.value,
            'metrics_count': len(self.health_metrics),
            'pending_upgrades': len(pending_upgrades),
            'in_progress_upgrades': len(in_progress_upgrades),
            'auto_upgrade_enabled': self.auto_upgrade_enabled,
            'maintenance_window': self.maintenance_window,
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }
        
    def get_health_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current health metrics"""
        return {
            name: {
                'value': metric.value,
                'unit': metric.unit,
                'status': metric.status.value,
                'threshold_warning': metric.threshold_warning,
                'threshold_critical': metric.threshold_critical,
                'timestamp': metric.timestamp.isoformat()
            }
            for name, metric in self.health_metrics.items()
        }
        
    def get_upgrade_status(self) -> List[Dict[str, Any]]:
        """Get status of all upgrade packages"""
        return [
            {
                'id': package.id,
                'name': package.name,
                'version': package.version,
                'description': package.description,
                'size_mb': package.size_mb,
                'priority': package.priority.name,
                'status': package.status.value,
                'progress': package.progress,
                'error_message': package.error_message,
                'created_at': package.created_at.isoformat()
            }
            for package in self.upgrade_packages.values()
        ]
        
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            record for record in self.health_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]