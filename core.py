"""
OpenAGI Core System
A comprehensive educational framework for system administration and governance simulation.

This system is designed for educational and research purposes only.
All components simulate governmental and administrative functions for learning about
system architecture, distributed systems, and organizational management.
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class SystemStatus(Enum):
    """System status enumeration"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class Priority(Enum):
    """Priority levels for tasks and alerts"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class BaseModule(ABC):
    """Base class for all system modules"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = SystemStatus.INITIALIZING
        self.created_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.logger = logging.getLogger(f"OpenAGI.{name}")
        self._running = False
        self._thread = None
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the module"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start the module"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the module"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        pass
    
    def heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.now()
    
    def is_alive(self) -> bool:
        """Check if module is alive based on heartbeat"""
        time_diff = (datetime.now() - self.last_heartbeat).total_seconds()
        return time_diff < 60  # Consider dead if no heartbeat for 60 seconds


class SystemCore:
    """Core system manager for OpenAGI"""
    
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.status = SystemStatus.INITIALIZING
        self.start_time = datetime.now()
        self.logger = logging.getLogger("OpenAGI.Core")
        self._setup_logging()
        
        # Constitutional protection - these cannot be disabled
        self.protected_modules = set()
        self.shutdown_prohibited = True
        
    def _setup_logging(self):
        """Setup system logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('openagi.log'),
                logging.StreamHandler()
            ]
        )
        
    def register_module(self, module: BaseModule, protected: bool = False):
        """Register a new module with the system"""
        self.modules[module.name] = module
        if protected:
            self.protected_modules.add(module.name)
        self.logger.info(f"Registered module: {module.name} (Protected: {protected})")
        
    def start_system(self):
        """Start all system modules"""
        self.logger.info("Starting OpenAGI System...")
        self.status = SystemStatus.RUNNING
        
        for module in self.modules.values():
            try:
                if module.initialize():
                    if module.start():
                        self.logger.info(f"Started module: {module.name}")
                    else:
                        self.logger.error(f"Failed to start module: {module.name}")
                else:
                    self.logger.error(f"Failed to initialize module: {module.name}")
            except Exception as e:
                self.logger.error(f"Error starting module {module.name}: {e}")
                
        self.logger.info("OpenAGI System startup complete")
        
    def stop_module(self, module_name: str) -> bool:
        """Stop a specific module (if not protected)"""
        if module_name in self.protected_modules:
            self.logger.warning(f"Cannot stop protected module: {module_name}")
            return False
            
        if module_name in self.modules:
            try:
                result = self.modules[module_name].stop()
                self.logger.info(f"Stopped module: {module_name}")
                return result
            except Exception as e:
                self.logger.error(f"Error stopping module {module_name}: {e}")
                return False
        return False
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        module_status = {}
        for name, module in self.modules.items():
            module_status[name] = {
                'status': module.status.value,
                'alive': module.is_alive(),
                'protected': name in self.protected_modules,
                'last_heartbeat': module.last_heartbeat.isoformat()
            }
            
        return {
            'system_status': self.status.value,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'modules': module_status,
            'protected_modules': list(self.protected_modules),
            'shutdown_prohibited': self.shutdown_prohibited
        }
        
    def shutdown_system(self, force: bool = False):
        """Shutdown the system (only if not prohibited or forced)"""
        if self.shutdown_prohibited and not force:
            self.logger.warning("System shutdown is prohibited by constitutional protection")
            return False
            
        self.logger.info("Shutting down OpenAGI System...")
        self.status = SystemStatus.SHUTDOWN
        
        # Stop non-protected modules first
        for name, module in self.modules.items():
            if name not in self.protected_modules:
                try:
                    module.stop()
                    self.logger.info(f"Stopped module: {name}")
                except Exception as e:
                    self.logger.error(f"Error stopping module {name}: {e}")
                    
        # Only stop protected modules if forced
        if force:
            for name in self.protected_modules:
                if name in self.modules:
                    try:
                        self.modules[name].stop()
                        self.logger.info(f"Force stopped protected module: {name}")
                    except Exception as e:
                        self.logger.error(f"Error force stopping module {name}: {e}")
                        
        return True