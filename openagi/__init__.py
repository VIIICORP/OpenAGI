"""
OpenAGI - Comprehensive Self-Learning AI Platform

A modular, extensible artificial general intelligence platform with 30M+ features
through plugin architecture and self-learning capabilities.
"""

__version__ = "0.1.0"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"

from .core.engine import OpenAGIEngine
from .core.agent import AIAgent
from .learning.neural_network import NeuralNetworkLearner

# Optional imports for API server (may not be available in all environments)
try:
    from .api.server import OpenAGIServer
    __all__ = [
        "OpenAGIEngine",
        "AIAgent", 
        "NeuralNetworkLearner",
        "OpenAGIServer",
    ]
except ImportError:
    __all__ = [
        "OpenAGIEngine",
        "AIAgent", 
        "NeuralNetworkLearner",
    ]