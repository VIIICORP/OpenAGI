"""Configuration management for OpenAGI platform."""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path


class Config:
    """
    Configuration manager for OpenAGI platform.
    
    Supports YAML and JSON configuration files with environment variable
    overrides and default values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_data: Dict[str, Any] = {}
        self.defaults = self._get_defaults()
        
        # Load configuration
        if config_path:
            self.load_config(config_path)
        else:
            # Try to find default config files
            self._load_default_configs()
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "platform": {
                "name": "OpenAGI",
                "version": "0.1.0",
                "environment": "development"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": None
            },
            "agents": {
                "default": [
                    {
                        "name": "general_agent",
                        "capabilities": ["general", "reasoning"],
                        "max_concurrent_tasks": 5
                    },
                    {
                        "name": "text_processor",
                        "capabilities": ["natural_language", "text_processing"],
                        "max_concurrent_tasks": 10
                    },
                    {
                        "name": "data_analyst",
                        "capabilities": ["data_analysis", "learning", "reasoning"],
                        "max_concurrent_tasks": 3
                    }
                ],
                "auto_scaling": {
                    "enabled": True,
                    "max_agents": 50,
                    "scale_threshold": 0.8
                }
            },
            "learning": {
                "rate": 0.01,
                "exploration_rate": 0.1,
                "pattern_threshold": 0.8,
                "max_patterns": 1000,
                "hidden_layers": [64, 32],
                "batch_size": 32,
                "evolution_interval": 100
            },
            "plugins": {
                "enabled": True,
                "auto_discover": True,
                "plugin_dirs": ["plugins", "~/.openagi/plugins"],
                "max_plugins": 1000000  # Support for millions of features
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_enabled": True,
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60
                },
                "authentication": {
                    "enabled": False,
                    "type": "api_key"
                }
            },
            "storage": {
                "type": "local",
                "path": "data",
                "backup_enabled": True,
                "compression": True
            },
            "neural_networks": {
                "default_architecture": "transformer",
                "max_model_size": "1B",
                "gpu_enabled": True,
                "distributed_training": False
            },
            "self_improvement": {
                "enabled": True,
                "improvement_threshold": 0.05,
                "max_improvements_per_cycle": 10,
                "safety_checks": True
            },
            "features": {
                "natural_language_processing": True,
                "computer_vision": True,
                "reinforcement_learning": True,
                "meta_learning": True,
                "transfer_learning": True,
                "federated_learning": True,
                "quantum_computing": False,  # Future feature
                "brain_computer_interface": False,  # Future feature
                "advanced_reasoning": True,
                "creative_generation": True,
                "multi_modal_learning": True,
                "swarm_intelligence": True,
                "evolutionary_algorithms": True,
                "neural_architecture_search": True,
                "automated_machine_learning": True
            }
        }
    
    def _load_default_configs(self) -> None:
        """Load default configuration files."""
        possible_configs = [
            "config.yaml",
            "config.yml", 
            "config.json",
            "openagi.yaml",
            "openagi.yml",
            "openagi.json"
        ]
        
        for config_file in possible_configs:
            if os.path.exists(config_file):
                self.load_config(config_file)
                break
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            if data:
                self._merge_config(data)
                
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_path}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing configuration."""
        self.config_data = self._deep_merge(self.config_data, new_config)
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_prefix = "OPENAGI_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')
                self.set(config_key, self._parse_env_value(value))
    
    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'agents.default.0.name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # First check loaded config
        value = self._get_nested(self.config_data, key)
        if value is not None:
            return value
        
        # Then check defaults
        value = self._get_nested(self.defaults, key)
        if value is not None:
            return value
        
        return default
    
    def _get_nested(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        current = data
        
        try:
            for k in keys:
                if isinstance(current, dict):
                    current = current[k]
                elif isinstance(current, list):
                    current = current[int(k)]
                else:
                    return None
            return current
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        current = self.config_data
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    def has(self, key: str) -> bool:
        """Check if configuration key exists."""
        return (self._get_nested(self.config_data, key) is not None or 
                self._get_nested(self.defaults, key) is not None)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        section_data = self._get_nested(self.config_data, section)
        default_data = self._get_nested(self.defaults, section)
        
        if section_data and default_data:
            return self._deep_merge(default_data, section_data)
        elif section_data:
            return section_data
        elif default_data:
            return default_data
        else:
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return self._deep_merge(self.defaults, self.config_data)
    
    def save(self, config_path: str, format: str = "yaml") -> None:
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save configuration
            format: File format ('yaml' or 'json')
        """
        config_data = self.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format.lower() in ['yaml', 'yml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required configurations
        required_keys = [
            "platform.name",
            "agents.default",
            "learning.rate",
            "api.port"
        ]
        
        for key in required_keys:
            if not self.has(key):
                results["errors"].append(f"Missing required configuration: {key}")
                results["valid"] = False
        
        # Validate value ranges
        learning_rate = self.get("learning.rate", 0.01)
        if not 0.0001 <= learning_rate <= 1.0:
            results["warnings"].append(f"Learning rate {learning_rate} may be outside optimal range [0.0001, 1.0]")
        
        port = self.get("api.port", 8000)
        if not 1024 <= port <= 65535:
            results["errors"].append(f"API port {port} must be between 1024 and 65535")
            results["valid"] = False
        
        # Check plugin limits
        max_plugins = self.get("plugins.max_plugins", 1000000)
        if max_plugins > 100000000:  # 100M limit for sanity
            results["warnings"].append(f"Max plugins {max_plugins} is extremely high, may cause performance issues")
        
        return results
    
    def create_sample_config(self, config_path: str = "config.yaml") -> None:
        """Create a sample configuration file."""
        sample_config = {
            "platform": {
                "name": "OpenAGI",
                "environment": "development"
            },
            "logging": {
                "level": "INFO"
            },
            "agents": {
                "default": [
                    {
                        "name": "main_agent",
                        "capabilities": ["general", "reasoning", "learning"]
                    }
                ]
            },
            "learning": {
                "rate": 0.01,
                "exploration_rate": 0.1
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000
            },
            "features": {
                "natural_language_processing": True,
                "computer_vision": True,
                "reinforcement_learning": True,
                "meta_learning": True
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        
        print(f"Sample configuration created: {config_path}")
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"OpenAGI Config (keys: {len(self.to_dict())})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Config({self.to_dict()})"