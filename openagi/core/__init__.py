"""
Core OpenAGI Platform Architecture

This module contains the core classes and interfaces for the OpenAGI platform,
including the main platform class, feature registry, and base interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FeatureInfo:
    """Information about a registered AI feature."""
    name: str
    category: str
    description: str
    version: str
    author: str
    tags: List[str]
    dependencies: List[str]
    
    
class AIFeature(ABC):
    """Base class for all AI features in the OpenAGI platform."""
    
    def __init__(self, name: str, category: str, description: str = ""):
        self.name = name
        self.category = category
        self.description = description
        self.version = "1.0.0"
        self.author = "OpenAGI"
        self.tags = []
        self.dependencies = []
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the AI feature with given parameters."""
        pass
    
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input parameters for the feature."""
        return True
    
    def get_info(self) -> FeatureInfo:
        """Get feature information."""
        return FeatureInfo(
            name=self.name,
            category=self.category,
            description=self.description,
            version=self.version,
            author=self.author,
            tags=self.tags,
            dependencies=self.dependencies
        )


class FeatureRegistry:
    """Registry for managing AI features in the OpenAGI platform."""
    
    def __init__(self):
        self._features: Dict[str, AIFeature] = {}
        self._categories: Dict[str, List[str]] = {}
        
    def register(self, feature: AIFeature) -> None:
        """Register a new AI feature."""
        if feature.name in self._features:
            logger.warning(f"Feature '{feature.name}' already registered. Overwriting.")
        
        self._features[feature.name] = feature
        
        if feature.category not in self._categories:
            self._categories[feature.category] = []
        
        if feature.name not in self._categories[feature.category]:
            self._categories[feature.category].append(feature.name)
        
        logger.info(f"Registered feature: {feature.name} ({feature.category})")
    
    def get_feature(self, name: str) -> Optional[AIFeature]:
        """Get a feature by name."""
        return self._features.get(name)
    
    def get_features_by_category(self, category: str) -> List[AIFeature]:
        """Get all features in a category."""
        feature_names = self._categories.get(category, [])
        return [self._features[name] for name in feature_names]
    
    def list_features(self) -> List[str]:
        """List all registered feature names."""
        return list(self._features.keys())
    
    def list_categories(self) -> List[str]:
        """List all feature categories."""
        return list(self._categories.keys())
    
    def search_features(self, query: str) -> List[AIFeature]:
        """Search features by name or description."""
        results = []
        query_lower = query.lower()
        
        for feature in self._features.values():
            if (query_lower in feature.name.lower() or 
                query_lower in feature.description.lower() or
                any(query_lower in tag.lower() for tag in feature.tags)):
                results.append(feature)
        
        return results
    
    def get_feature_count(self) -> int:
        """Get total number of registered features."""
        return len(self._features)
    
    def export_feature_list(self, format: str = "json") -> str:
        """Export feature list in specified format."""
        feature_data = []
        for feature in self._features.values():
            feature_data.append({
                "name": feature.name,
                "category": feature.category,
                "description": feature.description,
                "version": feature.version,
                "author": feature.author,
                "tags": feature.tags
            })
        
        if format.lower() == "json":
            return json.dumps(feature_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


class OpenAGI:
    """Main OpenAGI platform class providing access to all AI features."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.registry = FeatureRegistry()
        self.config = self._load_config(config_path)
        self._initialize_features()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load platform configuration."""
        default_config = {
            "logging_level": "INFO",
            "auto_load_features": True,
            "feature_timeout": 300,
            "enable_caching": True,
            "max_concurrent_features": 10
        }
        
        if config_path and Path(config_path).exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_features(self):
        """Initialize and register all available features."""
        if self.config.get("auto_load_features", True):
            self._load_all_features()
    
    def _load_all_features(self):
        """Load all available features from the features module."""
        try:
            from ..features import load_all_features
            load_all_features(self.registry)
            logger.info(f"Loaded {self.registry.get_feature_count()} features")
        except ImportError as e:
            logger.warning(f"Failed to load features module: {e}")
    
    def execute_feature(self, feature_name: str, *args, **kwargs) -> Any:
        """Execute a specific AI feature."""
        feature = self.registry.get_feature(feature_name)
        if not feature:
            raise ValueError(f"Feature '{feature_name}' not found")
        
        if not feature.validate_input(*args, **kwargs):
            raise ValueError(f"Invalid input for feature '{feature_name}'")
        
        try:
            logger.info(f"Executing feature: {feature_name}")
            result = feature.execute(*args, **kwargs)
            logger.info(f"Feature '{feature_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing feature '{feature_name}': {e}")
            raise
    
    def get_feature_info(self, feature_name: str) -> Optional[FeatureInfo]:
        """Get information about a specific feature."""
        feature = self.registry.get_feature(feature_name)
        return feature.get_info() if feature else None
    
    def list_available_features(self) -> Dict[str, List[str]]:
        """List all available features organized by category."""
        result = {}
        for category in self.registry.list_categories():
            result[category] = [f.name for f in self.registry.get_features_by_category(category)]
        return result
    
    def search_features(self, query: str) -> List[Dict[str, str]]:
        """Search for features matching the query."""
        features = self.registry.search_features(query)
        return [
            {
                "name": f.name,
                "category": f.category,
                "description": f.description
            }
            for f in features
        ]
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform statistics."""
        return {
            "total_features": self.registry.get_feature_count(),
            "categories": len(self.registry.list_categories()),
            "category_breakdown": {
                cat: len(self.registry.get_features_by_category(cat))
                for cat in self.registry.list_categories()
            },
            "version": "1.0.0"
        }