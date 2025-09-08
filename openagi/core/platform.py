#!/usr/bin/env python3
"""
OpenAGI Platform - Main Platform Class

This module contains the main OpenAGI platform class that serves as the
entry point for all AI features and capabilities.
"""

from typing import Dict, Any, List, Optional
import logging
import yaml
from pathlib import Path

from .registry import FeatureRegistry
from .feature import AIFeature

logger = logging.getLogger(__name__)


class OpenAGI:
    """
    Main OpenAGI Platform Class
    
    This class serves as the central hub for accessing and managing
    all AI features provided by the OpenAGI platform.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize OpenAGI platform.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.registry = FeatureRegistry()
        self._setup_logging()
        self._initialize_features()
        
        logger.info(f"OpenAGI platform initialized with {len(self.registry.features)} features")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "logging_level": "INFO",
            "auto_load_features": True,
            "feature_timeout": 300,
            "enable_caching": True,
            "max_concurrent_features": 10,
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    default_config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_path}: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.get("logging_level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _initialize_features(self):
        """Initialize and register available features."""
        if self.config.get("auto_load_features", True):
            # For now, we'll register a few sample features
            # In a full implementation, this would scan the features directory
            self.registry.register_sample_features()
    
    def list_features(self, category: Optional[str] = None) -> List[str]:
        """
        List available features.
        
        Args:
            category: Filter by feature category (optional)
            
        Returns:
            List of feature names
        """
        return self.registry.list_features(category)
    
    def get_feature(self, feature_name: str) -> Optional[AIFeature]:
        """
        Get a specific feature by name.
        
        Args:
            feature_name: Name of the feature to retrieve
            
        Returns:
            AIFeature instance or None if not found
        """
        return self.registry.get_feature(feature_name)
    
    def search_features(self, query: str) -> List[str]:
        """
        Search for features matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching feature names
        """
        return self.registry.search_features(query)
    
    def execute_feature(self, feature_name: str, **kwargs) -> Any:
        """
        Execute a feature with given parameters.
        
        Args:
            feature_name: Name of the feature to execute
            **kwargs: Feature-specific parameters
            
        Returns:
            Feature execution result
            
        Raises:
            ValueError: If feature not found
            Exception: If feature execution fails
        """
        feature = self.get_feature(feature_name)
        if not feature:
            raise ValueError(f"Feature '{feature_name}' not found")
        
        try:
            return feature.execute(**kwargs)
        except Exception as e:
            logger.error(f"Failed to execute feature '{feature_name}': {e}")
            raise
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform information.
        
        Returns:
            Dictionary containing platform information
        """
        return {
            "version": "1.0.1",
            "total_features": len(self.registry.features),
            "feature_categories": list(self.registry.get_categories()),
            "config": self.config,
        }