"""Test OpenAGI platform functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from openagi.core.platform import OpenAGIPlatform
from openagi.core.config import OpenAGIConfig


@pytest.fixture
def platform_config():
    """Create test configuration."""
    config = OpenAGIConfig()
    config.debugging.enable_auto_debug = False  # Disable for testing
    config.monitoring.enable_metrics = False    # Disable for testing
    return config


@pytest.fixture
def platform(platform_config):
    """Create test platform instance."""
    return OpenAGIPlatform(platform_config)


def test_platform_creation(platform):
    """Test platform creation."""
    assert platform.config is not None
    assert platform.logger is not None
    assert not platform._running


@pytest.mark.asyncio
async def test_platform_status(platform):
    """Test platform status."""
    status = platform.get_status()
    
    assert isinstance(status, dict)
    assert "running" in status
    assert "config" in status
    assert "components" in status
    assert status["running"] is False


@pytest.mark.asyncio 
async def test_platform_health_check(platform):
    """Test platform health check."""
    health_status = await platform._check_health()
    
    assert isinstance(health_status, dict)
    assert "healthy" in health_status
    assert "components" in health_status
    assert "timestamp" in health_status