"""Test debugging engine functionality."""

import pytest
from datetime import datetime
from openagi.debugging.engine import DebugEngine, DebugEvent, ErrorDetector
from openagi.core.config import OpenAGIConfig


@pytest.fixture
def debug_config():
    """Create test configuration for debugging."""
    config = OpenAGIConfig()
    config.debugging.enable_auto_debug = True
    config.debugging.debug_level = 2
    return config


@pytest.fixture
def debug_engine(debug_config):
    """Create test debug engine instance."""
    return DebugEngine(debug_config)


def test_debug_event_creation():
    """Test debug event creation."""
    event = DebugEvent(
        timestamp=datetime.now(),
        event_type="test_error",
        severity="medium",
        component="test",
        message="Test error message"
    )
    
    assert event.event_type == "test_error"
    assert event.severity == "medium"
    assert event.component == "test"
    assert event.resolved is False


def test_error_detector_creation(debug_config):
    """Test error detector creation."""
    detector = ErrorDetector(debug_config)
    
    assert detector.config == debug_config
    assert len(detector.error_patterns) > 0
    assert "memory_leak" in detector.error_patterns
    assert "deadlock" in detector.error_patterns


@pytest.mark.asyncio
async def test_debug_engine_initialization(debug_engine):
    """Test debug engine initialization."""
    await debug_engine.initialize()
    
    assert debug_engine.error_detector is not None
    assert debug_engine.self_healing is not None
    assert debug_engine.diagnostics is not None


@pytest.mark.asyncio
async def test_debug_engine_health_check(debug_engine):
    """Test debug engine health check."""
    await debug_engine.initialize()
    health = await debug_engine.health_check()
    
    assert isinstance(health, dict)
    assert "healthy" in health
    assert "active_issues" in health
    assert "components" in health