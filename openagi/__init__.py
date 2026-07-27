"""
OpenAGI Platform

A comprehensive artificial intelligence platform.
"""

from .chat import AGIChat
from .cli import main as cli_main

__version__ = "1.0.0"

__all__ = ["AGIChat", "cli_main"]
