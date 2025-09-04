"""
Tooling framework for the OpenAGI agent.

This package contains the base definition for tools and implementations
of various tools that allow the agent to interact with its environment
(e.g., web search, file system, code execution, voice capabilities).
"""

from .base import BaseTool
# Import tools conditionally to handle missing dependencies gracefully
__all__ = ["BaseTool"]

try:
    from .web_search import WebSearchTool
    __all__.append("WebSearchTool")
except ImportError:
    WebSearchTool = None

try:
    from .file_system import ReadFileTool, WriteFileTool, ListFilesTool
    __all__.extend(["ReadFileTool", "WriteFileTool", "ListFilesTool"])
except ImportError:
    ReadFileTool = WriteFileTool = ListFilesTool = None

try:
    from .code_execution import ExecutePythonCodeTool
    __all__.append("ExecutePythonCodeTool")
except ImportError:
    ExecutePythonCodeTool = None

try:
    from .audio_generation import GenerateSoundWaveTool
    __all__.append("GenerateSoundWaveTool")
except ImportError:
    GenerateSoundWaveTool = None