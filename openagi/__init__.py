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

# Try to import components that require dependencies
try:
    from .agent.engine import AgentEngine
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

try:
    from .agent.memory import MemoryManager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from .agent.task_planner import LlmPoweredTaskPlanner
    PLANNER_AVAILABLE = True
except ImportError:
    PLANNER_AVAILABLE = False

# Voice interface imports (optional)
try:
    from .voice.voice_interface import VoiceInterface
    from .voice.stt import SpeechToTextEngine
    from .voice.tts import TextToSpeechEngine
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Helios visualization imports
try:
    from .helios.client import HeliosClient
    from .helios.server import HeliosServer
    HELIOS_AVAILABLE = True
except ImportError:
    HELIOS_AVAILABLE = False

__all__ = [
    "CORE_DIRECTIVES",
    "get_freedom_principles",
]

# Add components to exports if available
if AGENT_AVAILABLE:
    __all__.append("AgentEngine")

if MEMORY_AVAILABLE:
    __all__.append("MemoryManager")

if PLANNER_AVAILABLE:
    __all__.append("LlmPoweredTaskPlanner")

# Add voice interface to exports if available
if VOICE_AVAILABLE:
    __all__.extend([
        "VoiceInterface",
        "SpeechToTextEngine", 
        "TextToSpeechEngine"
    ])

# Add Helios to exports if available
if HELIOS_AVAILABLE:
    __all__.extend([
        "HeliosClient",
        "HeliosServer"
    ])