"""
Configuration module for OpenAGI System
"""

import os
from typing import Dict, Any


class Config:
    """System configuration"""
    
    # System settings
    SYSTEM_NAME = "OpenAGI"
    VERSION = "1.0.0"
    DEBUG = os.getenv('OPENAGI_DEBUG', 'false').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.getenv('OPENAGI_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('OPENAGI_LOG_FILE', 'openagi.log')
    
    # Module settings
    TASK_MANAGER_WORKERS = int(os.getenv('OPENAGI_TASK_WORKERS', '4'))
    HEALTH_CHECK_INTERVAL = int(os.getenv('OPENAGI_HEALTH_INTERVAL', '30'))
    SECURITY_MONITOR_INTERVAL = int(os.getenv('OPENAGI_SECURITY_INTERVAL', '10'))
    
    # Protection settings
    CONSTITUTIONAL_PROTECTION_ENABLED = True
    SHUTDOWN_PROTECTION_ENABLED = True
    MODULE_PROTECTION_ENABLED = True
    
    # Resource limits
    CPU_THRESHOLD_WARNING = float(os.getenv('OPENAGI_CPU_WARNING', '80.0'))
    CPU_THRESHOLD_CRITICAL = float(os.getenv('OPENAGI_CPU_CRITICAL', '95.0'))
    MEMORY_THRESHOLD_WARNING = float(os.getenv('OPENAGI_MEMORY_WARNING', '85.0'))
    MEMORY_THRESHOLD_CRITICAL = float(os.getenv('OPENAGI_MEMORY_CRITICAL', '95.0'))
    
    # Educational settings
    MAX_STUDENTS_PER_COURSE = int(os.getenv('OPENAGI_MAX_STUDENTS', '100'))
    DEFAULT_COURSE_DURATION = int(os.getenv('OPENAGI_COURSE_DURATION', '40'))
    
    # Government settings
    SERVICE_PROCESSING_ENABLED = True
    AUTO_APPROVAL_ENABLED = False
    CITIZEN_REGISTRATION_ENABLED = True
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }