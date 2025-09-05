"""Core module initialization."""

try:
    from openagi.core.platform import OpenAGIPlatform
    from openagi.core.config import OpenAGIConfig
    from openagi.core.logger import get_openagi_logger
    __all__ = ["OpenAGIPlatform", "OpenAGIConfig", "get_openagi_logger"]
except ImportError:
    # Handle import errors gracefully during initial setup
    __all__ = []