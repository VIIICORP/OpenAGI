#!/usr/bin/env python3
"""
OpenAGI Configuration Utilities

This module provides configuration loading and validation utilities.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigurationError


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file or return defaults.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If configuration file is invalid
    """
    default_config = {
        "logging_level": "INFO",
        "auto_load_features": True,
        "feature_timeout": 300,
        "enable_caching": True,
        "max_concurrent_features": 10,
        "nlp": {
            "default_language": "en",
            "max_text_length": 10000
        },
        "computer_vision": {
            "default_image_format": "RGB",
            "max_image_size": [1920, 1080]
        },
        "machine_learning": {
            "default_random_state": 42,
            "cross_validation_folds": 5
        }
    }
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    default_config.update(file_config)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {config_path}: {e}")
    
    return default_config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    required_keys = ["logging_level", "auto_load_features", "feature_timeout"]
    
    for key in required_keys:
        if key not in config:
            raise ConfigurationError(f"Required configuration key '{key}' is missing")
    
    # Validate logging level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config["logging_level"].upper() not in valid_levels:
        raise ConfigurationError(f"Invalid logging level: {config['logging_level']}")
    
    # Validate timeout
    if not isinstance(config["feature_timeout"], (int, float)) or config["feature_timeout"] <= 0:
        raise ConfigurationError("feature_timeout must be a positive number")
    
    # Validate max_concurrent_features
    if "max_concurrent_features" in config:
        if not isinstance(config["max_concurrent_features"], int) or config["max_concurrent_features"] <= 0:
            raise ConfigurationError("max_concurrent_features must be a positive integer")
    
    return True