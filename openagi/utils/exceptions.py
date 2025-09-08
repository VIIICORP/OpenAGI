#!/usr/bin/env python3
"""
OpenAGI Custom Exceptions

This module defines custom exceptions used throughout the OpenAGI platform.
"""


class OpenAGIError(Exception):
    """Base exception for all OpenAGI-related errors."""
    pass


class FeatureError(OpenAGIError):
    """Exception raised when there's an error with AI features."""
    pass


class ConfigurationError(OpenAGIError):
    """Exception raised when there's a configuration error."""
    pass


class SafetyError(OpenAGIError):
    """Exception raised when safety validation fails."""
    pass


class ModelError(OpenAGIError):
    """Exception raised when AI model operations fail."""
    pass


class ValidationError(OpenAGIError):
    """Exception raised when input validation fails."""
    pass