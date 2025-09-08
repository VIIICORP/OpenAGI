"""
Configuration Manager Module

This module handles all configuration management for the OpenAGI platform,
including dynamic configuration updates, validation, and persistence.
"""

import json
import logging
import os
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import threading
from copy import deepcopy


class ConfigManager:
    """
    Comprehensive configuration management system for OpenAGI.
    
    Supports multiple configuration formats, dynamic updates, validation,
    and hierarchical configuration structures.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration state
        self._config: Dict[str, Any] = {}
        self._default_config: Dict[str, Any] = {}
        self._config_lock = threading.RLock()
        self._config_history: List[Dict[str, Any]] = []
        
        # Configuration files
        self.config_path = Path(config_path) if config_path else Path("openagi_config.yaml")
        self.default_config_path = Path("default_config.yaml")
        
        # Initialize with default configuration
        self._load_default_config()
        
        # Load user configuration if exists
        if self.config_path.exists():
            self._load_config()
        else:
            self._save_config()
        
        self.logger.info(f"Configuration manager initialized with config: {self.config_path}")
    
    def _load_default_config(self) -> None:
        """Load default configuration values."""
        self._default_config = {
            # Platform settings
            "platform": {
                "name": "OpenAGI",
                "version": "1.0.0",
                "environment": "production",
                "debug": False,
                "log_level": "INFO",
                "max_agents": 1000,
                "feature_flags": {
                    "self_healing": True,
                    "monitoring": True,
                    "recovery": True,
                    "auto_scaling": True,
                    "predictive_analysis": True
                }
            },
            
            # Monitoring configuration
            "monitoring": {
                "enabled": True,
                "interval": 5,
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "disk_threshold": 90.0,
                "agent_timeout": 60.0,
                "max_history": 1000,
                "alert_thresholds": {
                    "response_time": 5.0,
                    "error_rate": 10.0,
                    "success_rate": 90.0
                }
            },
            
            # Self-healing configuration
            "self_healing": {
                "enabled": True,
                "auto_recovery": True,
                "learning_enabled": True,
                "max_retry_attempts": 3,
                "recovery_timeout": 300,
                "healing_strategies": [
                    "restart", "rollback", "scale_up", "scale_down",
                    "reconfigure", "failover", "optimize", "repair"
                ],
                "proactive_healing": True,
                "prediction_window": 600
            },
            
            # Recovery configuration
            "recovery": {
                "enabled": True,
                "backup_dir": "./backups",
                "max_backups": 50,
                "backup_interval": 3600,
                "auto_backup": True,
                "compression_enabled": True,
                "encryption_enabled": False,
                "retention_days": 30
            },
            
            # API configuration
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "max_request_size": "10MB",
                "timeout": 30,
                "cors_enabled": True,
                "swagger_enabled": True,
                "versioning": "v1"
            }
        }
        
        # Apply default configuration
        with self._config_lock:
            self._config = deepcopy(self._default_config)
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)
            
            # Merge with default configuration
            with self._config_lock:
                self._config = self._merge_configs(self._default_config, user_config)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            # Use default configuration on error
            with self._config_lock:
                self._config = deepcopy(self._default_config)
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._config_lock:
                config_to_save = deepcopy(self._config)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_to_save, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_to_save, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with default configuration."""
        result = deepcopy(default)
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        with self._config_lock:
            keys = key.split('.')
            value = self._config
            
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set configuration value using dot notation."""
        with self._config_lock:
            # Save current config to history
            self._config_history.append(deepcopy(self._config))
            
            # Limit history size
            if len(self._config_history) > 10:
                self._config_history.pop(0)
            
            keys = key.split('.')
            config = self._config
            
            # Navigate to parent
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set value
            config[keys[-1]] = value
        
        if save:
            self._save_config()
        
        self.logger.info(f"Configuration updated: {key} = {value}")
    
    def exists(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key) is not None
    
    def export_config(self) -> Dict[str, Any]:
        """Export entire configuration."""
        with self._config_lock:
            return deepcopy(self._config)
    
    def import_config(self, config: Dict[str, Any], save: bool = True) -> None:
        """Import configuration from dictionary."""
        with self._config_lock:
            # Save current config to history
            self._config_history.append(deepcopy(self._config))
            
            # Merge with default to ensure all required keys exist
            self._config = self._merge_configs(self._default_config, config)
        
        if save:
            self._save_config()
        
        self.logger.info("Configuration imported")
    
    def validate_config(self) -> List[str]:
        """Validate current configuration and return list of issues."""
        errors = []
        
        with self._config_lock:
            config = self._config
        
        # Validate required sections
        required_sections = ['platform', 'monitoring', 'self_healing', 'recovery']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate specific settings
        try:
            # Monitoring thresholds
            if config.get('monitoring', {}).get('cpu_threshold', 0) > 100:
                errors.append("CPU threshold cannot exceed 100%")
            
            if config.get('monitoring', {}).get('memory_threshold', 0) > 100:
                errors.append("Memory threshold cannot exceed 100%")
            
            # API port
            api_port = config.get('api', {}).get('port', 8000)
            if not isinstance(api_port, int) or api_port < 1 or api_port > 65535:
                errors.append("API port must be between 1 and 65535")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about the configuration."""
        with self._config_lock:
            config_size = len(str(self._config))
            history_size = len(self._config_history)
        
        return {
            "config_file": str(self.config_path),
            "config_exists": self.config_path.exists(),
            "config_size_bytes": config_size,
            "history_versions": history_size,
            "last_modified": self.config_path.stat().st_mtime if self.config_path.exists() else None,
            "validation_errors": self.validate_config()
        }