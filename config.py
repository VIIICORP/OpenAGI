#!/usr/bin/env python3
"""
Configuration module for OpenAGI Platform
"""

import os
from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class Config:
    """OpenAGI Platform Configuration"""
    
    # System settings
    SYSTEM_NAME = "OpenAGI"
    VERSION = "1.0.0"
    DEBUG = os.getenv('OPENAGI_DEBUG', 'false').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.getenv('OPENAGI_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('OPENAGI_LOG_FILE', 'openagi.log')
    
    # Feature settings
    AUTO_LOAD_FEATURES = True
    FEATURE_TIMEOUT = int(os.getenv('OPENAGI_FEATURE_TIMEOUT', '300'))
    MAX_CONCURRENT_FEATURES = int(os.getenv('OPENAGI_MAX_CONCURRENT', '10'))
    ENABLE_CACHING = True
    
    # API settings
    API_HOST = os.getenv('OPENAGI_API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('OPENAGI_API_PORT', '8000'))
    API_RATE_LIMIT = int(os.getenv('OPENAGI_RATE_LIMIT', '1000'))
    
    # NLP settings
    NLP_DEFAULT_LANGUAGE = "en"
    NLP_MAX_TEXT_LENGTH = 10000
    
    # Computer Vision settings
    CV_DEFAULT_IMAGE_FORMAT = "RGB"
    CV_MAX_IMAGE_SIZE = [1920, 1080]
    
    # Machine Learning settings
    ML_DEFAULT_RANDOM_STATE = 42
    ML_CROSS_VALIDATION_FOLDS = 5
    
    # Audio Processing settings
    AUDIO_DEFAULT_SAMPLE_RATE = 44100
    AUDIO_MAX_LENGTH = 300
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = "config.yaml"
            
        config_file = Path(config_path)
        if not config_file.exists():
            return cls.get_default_config()
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return cls.get_default_config()
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'logging_level': cls.LOG_LEVEL,
            'auto_load_features': cls.AUTO_LOAD_FEATURES,
            'feature_timeout': cls.FEATURE_TIMEOUT,
            'enable_caching': cls.ENABLE_CACHING,
            'max_concurrent_features': cls.MAX_CONCURRENT_FEATURES,
            'nlp': {
                'default_language': cls.NLP_DEFAULT_LANGUAGE,
                'max_text_length': cls.NLP_MAX_TEXT_LENGTH
            },
            'computer_vision': {
                'default_image_format': cls.CV_DEFAULT_IMAGE_FORMAT,
                'max_image_size': cls.CV_MAX_IMAGE_SIZE
            },
            'machine_learning': {
                'default_random_state': cls.ML_DEFAULT_RANDOM_STATE,
                'cross_validation_folds': cls.ML_CROSS_VALIDATION_FOLDS
            },
            'audio_processing': {
                'default_sample_rate': cls.AUDIO_DEFAULT_SAMPLE_RATE,
                'max_audio_length': cls.AUDIO_MAX_LENGTH
            },
            'api': {
                'rate_limit': cls.API_RATE_LIMIT,
                'timeout': 30
            },
            'cache': {
                'enabled': cls.ENABLE_CACHING,
                'max_size': "1GB",
                'ttl': 3600
            }
        }
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }