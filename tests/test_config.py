"""Test configuration for OpenAGI."""

import pytest
from openagi.core.config import OpenAGIConfig


def test_default_config():
    """Test default configuration creation."""
    config = OpenAGIConfig()
    
    assert config.app_name == "OpenAGI"
    assert config.app_version == "1.0.0"
    assert config.environment == "development"
    assert config.debugging.enable_auto_debug is True
    assert config.monitoring.enable_metrics is True
    assert config.api.host == "127.0.0.1"
    assert config.api.port == 8000


def test_config_to_dict():
    """Test configuration to dictionary conversion."""
    config = OpenAGIConfig()
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert "app_name" in config_dict
    assert "debugging" in config_dict
    assert "monitoring" in config_dict
    assert "api" in config_dict


@pytest.mark.asyncio
async def test_config_directories():
    """Test that configuration creates required directories."""
    config = OpenAGIConfig()
    
    # Directories should be created during initialization
    assert config.data_dir.exists()
    assert config.ai.model_cache_dir.exists()