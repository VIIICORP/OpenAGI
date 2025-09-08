#!/usr/bin/env python3
"""
OpenAGI Platform - Main Package

Comprehensive OpenAGI platform with 14,000+ AI features
"""

__version__ = "1.0.1"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"
__description__ = "Comprehensive OpenAGI platform with 14,000+ AI features"

from .core.platform import OpenAGI
from .core.registry import FeatureRegistry
from .core.feature import AIFeature

__all__ = [
    "OpenAGI",
    "FeatureRegistry", 
    "AIFeature",
    "__version__",
]