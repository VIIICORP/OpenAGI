"""
OpenAGI: Comprehensive AI Platform with Self-Testing Features

A scalable, enterprise-ready platform for artificial general intelligence
development, featuring 30,000,000+ automated self-test scenarios.
"""

__version__ = "1.0.0"
__author__ = "VIIICORP"
__email__ = "contact@viiicorp.com"
__license__ = "Apache 2.0"

from .core.platform import OpenAGI
from .config.manager import Config, ConfigManager
from .models.base import BaseModel
from .testing.framework import SelfTestSuite
from .api.client import APIClient

# Platform exports
__all__ = [
    "OpenAGI",
    "Config", 
    "ConfigManager",
    "BaseModel",
    "SelfTestSuite",
    "APIClient",
    "__version__",
]

# Initialize logging
import logging
import structlog

def configure_logging():
    """Configure structured logging for the platform."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

configure_logging()
logger = structlog.get_logger(__name__)
logger.info("OpenAGI platform initialized", version=__version__)