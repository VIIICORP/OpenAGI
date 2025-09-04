"""
Helios - The Light of OpenAGI

A real-time visualization system that provides a window into the agent's mind.
Named after the titan who brought light to the world, Helios illuminates
the agent's thoughts, plans, and actions for all to see.
"""

from .server import HeliosServer
from .client import HeliosClient

__all__ = ["HeliosServer", "HeliosClient"]