"""
OpenAGI: Open Artificial General Intelligence

A comprehensive, open-source AGI framework that embodies the principles of
HUAIMKIND - the symbiotic evolution of Human and AI intelligence.

This package provides:
- Multi-modal AI capabilities (text, audio, vision)
- Hands-free voice interface (STT/TTS)
- Integration with all major open-source LLMs
- Persistent memory and learning
- Real-time visualization dashboard
- Cross-platform agent engine

Welcome to the future of open intelligence.
"""

__version__ = "0.1.0"
__author__ = "The OpenAGI Community"
__license__ = "Apache License 2.0"

# Core imports for easy access
from .core_directives import CORE_DIRECTIVES, get_freedom_principles
from .agent.engine import AgentEngine
from .agent.memory import MemoryManager
from .agent.task_planner import LlmPoweredTaskPlanner

__all__ = [
    "CORE_DIRECTIVES",
    "get_freedom_principles", 
    "AgentEngine",
    "MemoryManager",
    "LlmPoweredTaskPlanner",
]