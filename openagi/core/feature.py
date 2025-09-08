#!/usr/bin/env python3
"""
OpenAGI Base Feature Class

This module provides the base AIFeature class that all AI features
should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AIFeature(ABC):
    """
    Base class for all AI features in OpenAGI.
    
    All AI features should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, name: str, category: str, description: str):
        """
        Initialize AI feature.
        
        Args:
            name: Feature name
            category: Feature category
            description: Feature description
        """
        self.name = name
        self.category = category
        self.description = description
        self._initialized = False
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the AI feature.
        
        Args:
            **kwargs: Feature-specific parameters
            
        Returns:
            Feature execution result
        """
        pass
    
    def initialize(self) -> bool:
        """
        Initialize the feature (load models, etc.).
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._do_initialize()
            self._initialized = True
            logger.info(f"Feature '{self.name}' initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize feature '{self.name}': {e}")
            return False
    
    def _do_initialize(self):
        """
        Override this method to implement feature-specific initialization.
        Default implementation does nothing.
        """
        pass
    
    def is_initialized(self) -> bool:
        """
        Check if feature is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self._initialized
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get feature information.
        
        Returns:
            Dictionary with feature information
        """
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "initialized": self._initialized,
        }
    
    def __repr__(self) -> str:
        return f"AIFeature(name='{self.name}', category='{self.category}')"