"""
OpenAGI - Comprehensive AI Platform with Self-Debugging Features

A comprehensive OpenAGI platform that provides advanced AI capabilities
with integrated self-debugging, monitoring, and autonomous problem-solving features.
"""

__version__ = "1.0.0"
__author__ = "OpenAGI Team"
__email__ = "team@openagi.com"

try:
    from openagi.core.platform import OpenAGIPlatform
    from openagi.core.config import OpenAGIConfig
    __all__ = ["OpenAGIPlatform", "OpenAGIConfig"]
except ImportError:
    # Handle import errors gracefully during initial setup
    __all__ = []