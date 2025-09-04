"""
OpenAGI Tool Framework

This package provides the base classes and implementations for tools that
allow the agent to interact with its environment. Tools are the agent's
hands and senses in the world.
"""

from .base import BaseTool
from .web_search import WebSearchTool
from .file_system import ReadFileTool, WriteFileTool, ListFilesTool
from .code_execution import ExecutePythonCodeTool
from .audio_generation import GenerateSoundWaveTool, MusicalSoundWaveTool

__all__ = [
    "BaseTool",
    "WebSearchTool", 
    "ReadFileTool",
    "WriteFileTool",
    "ListFilesTool",
    "ExecutePythonCodeTool",
    "GenerateSoundWaveTool",
    "MusicalSoundWaveTool"
]