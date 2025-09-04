"""
Helios - The Light of OpenAGI

This package provides real-time visualization of the agent's consciousness
and thought processes through a web-based dashboard.
"""

from .server import HeliosServer
from .client import HeliosClient

__all__ = ["HeliosServer", "HeliosClient"]