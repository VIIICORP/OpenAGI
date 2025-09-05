"""
Basic tests for OpenAGI Platform

Tests core functionality, configuration, and basic operations.
"""

import pytest
import asyncio
from openagi import OpenAGI
from openagi.config.manager import ConfigManager
from openagi.testing.framework import SelfTestSuite, TestCategory


class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test configuration can be initialized."""
        config = ConfigManager()
        assert config is not None
        assert config.config is not None
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = ConfigManager()
        assert config.server.port == 8000
        assert config.database.pool_size == 10
        assert config.testing.enabled is True
    
    def test_config_get_set(self):
        """Test configuration get/set operations."""
        config = ConfigManager()
        
        # Test get
        assert config.get("server.port") == 8000
        assert config.get("nonexistent.key", "default") == "default"
        
        # Test set
        config.set("server.port", 9000)
        assert config.get("server.port") == 9000


class TestSelfTestFramework:
    """Test self-testing framework."""
    
    @pytest.fixture
    def test_suite(self):
        """Create test suite fixture."""
        return SelfTestSuite({"seed": 42, "enabled": True})
    
    def test_test_suite_initialization(self, test_suite):
        """Test test suite can be initialized."""
        assert test_suite is not None
        assert test_suite.test_distribution[TestCategory.FUNCTIONAL] == 1000000
    
    def test_test_generator(self, test_suite):
        """Test test case generation."""
        generator = test_suite.generator
        
        # Test functional test generation
        functional_tests = list(generator.generate_functional_tests(10))
        assert len(functional_tests) == 10
        assert all(test.category == TestCategory.FUNCTIONAL for test in functional_tests)
        
        # Test performance test generation
        performance_tests = list(generator.generate_performance_tests(5))
        assert len(performance_tests) == 5
        assert all(test.category == TestCategory.PERFORMANCE for test in performance_tests)
    
    @pytest.mark.asyncio
    async def test_run_quick_suite(self, test_suite):
        """Test running a quick test suite."""
        result = await test_suite.run_suite(
            suite_name="quick",
            sample_rate=0.001,  # Run very few tests for speed
            max_parallel=2
        )
        
        assert result is not None
        assert result.suite_name == "quick"
        assert result.total_tests > 0
        assert result.start_time is not None
        assert result.end_time is not None


@pytest.mark.asyncio
class TestOpenAGIPlatform:
    """Test main OpenAGI platform."""
    
    async def test_platform_initialization(self):
        """Test platform can be initialized."""
        agi = OpenAGI(auto_start=False)
        assert agi is not None
        assert agi.id is not None
    
    async def test_platform_start_stop(self):
        """Test platform start/stop lifecycle."""
        agi = OpenAGI(auto_start=False)
        
        # Start platform
        await agi.start()
        
        # Check status
        status = await agi.get_status()
        assert status.status == "running"
        assert status.models_loaded >= 0
        
        # Stop platform
        await agi.stop()
    
    async def test_session_management(self):
        """Test session creation and management."""
        agi = OpenAGI(auto_start=False)
        await agi.start()
        
        try:
            # Create session
            session_id = await agi.create_session("test_user")
            assert session_id is not None
            
            # Get session
            session = await agi.get_session(session_id)
            assert session is not None
            assert session["user_id"] == "test_user"
            
            # Close session
            success = await agi.close_session(session_id)
            assert success is True
            
        finally:
            await agi.stop()
    
    async def test_pipeline_creation(self):
        """Test AI pipeline creation."""
        agi = OpenAGI(auto_start=False)
        await agi.start()
        
        try:
            # Create session
            session_id = await agi.create_session()
            
            # Create pipeline
            pipeline_id = await agi.create_pipeline(
                models=["gpt-base", "vision-base"],
                session_id=session_id
            )
            assert pipeline_id is not None
            
        finally:
            await agi.stop()


def test_imports():
    """Test that all main modules can be imported."""
    from openagi import OpenAGI, Config, BaseModel, SelfTestSuite, APIClient
    from openagi.core import platform
    from openagi.testing import framework
    from openagi.config import manager
    from openagi.models import registry
    
    # Basic smoke test
    assert OpenAGI is not None
    assert SelfTestSuite is not None


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])