#!/usr/bin/env python3
"""
OpenAGI Feature Registry - Feature Management and Discovery

This module provides the FeatureRegistry class for managing and discovering
AI features within the OpenAGI platform.
"""

from typing import Dict, List, Optional, Set
import logging
from abc import ABC, abstractmethod

from .feature import AIFeature

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """
    Feature Registry for managing AI features.
    
    This class handles registration, discovery, and management of all
    AI features available in the OpenAGI platform.
    """
    
    def __init__(self):
        """Initialize the feature registry."""
        self.features: Dict[str, AIFeature] = {}
        self._categories: Set[str] = set()
        
    def register_feature(self, feature: AIFeature):
        """
        Register a new feature.
        
        Args:
            feature: AIFeature instance to register
        """
        self.features[feature.name] = feature
        self._categories.add(feature.category)
        logger.debug(f"Registered feature: {feature.name}")
    
    def get_feature(self, name: str) -> Optional[AIFeature]:
        """
        Get a feature by name.
        
        Args:
            name: Feature name
            
        Returns:
            AIFeature instance or None if not found
        """
        return self.features.get(name)
    
    def list_features(self, category: Optional[str] = None) -> List[str]:
        """
        List available features.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of feature names
        """
        if category:
            return [name for name, feature in self.features.items() 
                   if feature.category == category]
        return list(self.features.keys())
    
    def search_features(self, query: str) -> List[str]:
        """
        Search features by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching feature names
        """
        query_lower = query.lower()
        results = []
        
        for name, feature in self.features.items():
            if (query_lower in name.lower() or 
                query_lower in feature.description.lower()):
                results.append(name)
        
        return results
    
    def get_categories(self) -> Set[str]:
        """
        Get all available feature categories.
        
        Returns:
            Set of category names
        """
        return self._categories.copy()
    
    def register_sample_features(self):
        """Register some sample features for demonstration."""
        from .sample_features import (
            TextTokenizerFeature,
            SentimentAnalysisFeature,
            ImageClassificationFeature
        )
        
        # Register sample features
        self.register_feature(TextTokenizerFeature())
        self.register_feature(SentimentAnalysisFeature()) 
        self.register_feature(ImageClassificationFeature())
        
        logger.info(f"Registered {len(self.features)} sample features")