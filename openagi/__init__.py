"""
OpenAGI - Comprehensive AI Platform with 14,000+ Features

A unified platform providing extensive AI capabilities across multiple domains
including NLP, Computer Vision, Machine Learning, Audio Processing, and more.
"""

__version__ = "1.0.0"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"

from .core import OpenAGI, FeatureRegistry
from .features import *

__all__ = [
    "OpenAGI",
    "FeatureRegistry",
    "__version__",
]