"""
OpenAGI - Open-source AGI platform with 20,000+ AI models and features.

This package provides a comprehensive platform for integrating and using
thousands of open-source AI models across various domains including:
- Large Language Models
- Computer Vision
- Audio Processing  
- Multimodal AI
- Embedding Models
- Agent Frameworks
- RAG Systems

Example:
    >>> from openagi import OpenAGI
    >>> agi = OpenAGI()
    >>> models = agi.models.list(category="llm")
    >>> llm = agi.models.load("llama2-7b-chat")
    >>> response = llm.generate("Hello, world!")
"""

__version__ = "0.1.0"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"
__license__ = "Apache-2.0"

from .core.platform import OpenAGI
from .core.config import Config
from .models.registry import ModelRegistry
from .agents.base import Agent
from .api.client import Client

__all__ = [
    "OpenAGI",
    "Config", 
    "ModelRegistry",
    "Agent",
    "Client",
]