"""Configuration management for OpenAGI."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration manager for OpenAGI platform.
    
    Handles loading and managing configuration from files,
    environment variables, and runtime parameters.
    """
    
    DEFAULT_CONFIG = {
        "openagi": {
            "models": {
                "cache_dir": "./models",
                "auto_download": True,
                "gpu_memory_fraction": 0.8,
                "max_concurrent_loads": 3,
                "default_device": "auto"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "timeout": 300,
                "max_request_size": "100MB"
            },
            "storage": {
                "backend": "local",
                "path": "./data",
                "max_size": "10GB",
                "compression": True
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9090,
                "log_level": "INFO",
                "retention_days": 30
            },
            "agents": {
                "max_concurrent": 10,
                "default_timeout": 600,
                "memory_limit": "2GB"
            },
            "security": {
                "api_key_required": False,
                "rate_limit": 1000,
                "cors_enabled": True
            }
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
            **kwargs: Additional configuration overrides
        """
        self._config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_path:
            self._load_from_file(config_path)
            
        # Load from environment variables
        self._load_from_env()
        
        # Apply runtime overrides
        if kwargs:
            self._apply_overrides(kwargs)
            
    def _load_from_file(self, config_path: str):
        """Load configuration from YAML file."""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                file_config = yaml.safe_load(f)
                self._deep_merge(self._config, file_config)
                
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "OPENAGI_MODELS_CACHE_DIR": "openagi.models.cache_dir",
            "OPENAGI_API_HOST": "openagi.api.host", 
            "OPENAGI_API_PORT": "openagi.api.port",
            "OPENAGI_STORAGE_BACKEND": "openagi.storage.backend",
            "OPENAGI_STORAGE_PATH": "openagi.storage.path",
            "OPENAGI_GPU_MEMORY": "openagi.models.gpu_memory_fraction",
            "OPENAGI_LOG_LEVEL": "openagi.monitoring.log_level",
            "OPENAGI_API_KEY": "openagi.security.api_key"
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(config_path, value)
                
    def _apply_overrides(self, overrides: Dict[str, Any]):
        """Apply runtime configuration overrides."""
        self._deep_merge(self._config, overrides)
        
    def _deep_merge(self, base: Dict, update: Dict):
        """Recursively merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
                
    def _set_nested(self, path: str, value: Any):
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
                
        current[keys[-1]] = value
        
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., "openagi.models.cache_dir")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
            
    def set(self, path: str, value: Any):
        """
        Set a configuration value using dot notation.
        
        Args:
            path: Configuration path
            value: Value to set
        """
        self._set_nested(path, value)
        
    def to_dict(self) -> Dict[str, Any]:
        """Return the full configuration as a dictionary."""
        return self._config.copy()
        
    def save(self, path: str):
        """
        Save current configuration to a YAML file.
        
        Args:
            path: Output file path
        """
        with open(path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)