"""
OpenAGI - Comprehensive OpenAGI platform with 30M+ Self Healing AI features

This module provides the core OpenAGI platform with advanced self-healing AI capabilities.
"""

__version__ = "1.0.0"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"

from .core import OpenAGI
from .self_healing import SelfHealingAI
from .monitoring import HealthMonitor
from .recovery import RecoveryManager
from .config import ConfigManager

__all__ = [
    "OpenAGI",
    "SelfHealingAI", 
    "HealthMonitor",
    "RecoveryManager",
    "ConfigManager",
]