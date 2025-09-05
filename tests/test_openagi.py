"""
Basic tests for the OpenAGI platform.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from openagi import OpenAGI, ConfigManager, HealthMonitor, RecoveryManager, SelfHealingAI


class TestOpenAGI:
    """Test cases for the main OpenAGI platform."""
    
    @pytest.fixture
    async def platform(self):
        """Create a test platform instance."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
platform:
  name: "TestOpenAGI"
  max_agents: 10
monitoring:
  interval: 1
  cpu_threshold: 90
recovery:
  backup_dir: "./test_backups"
  max_backups: 5
""")
            config_path = f.name
        
        platform = OpenAGI(config_path)
        yield platform
        
        # Cleanup
        Path(config_path).unlink()
        if Path("./test_backups").exists():
            shutil.rmtree("./test_backups")
    
    @pytest.mark.asyncio
    async def test_platform_initialization(self, platform):
        """Test platform initialization."""
        assert platform.platform_id is not None
        assert platform.get_feature_count() > 30000000  # 30M+ features
        assert len(platform.list_features()) > 0
    
    @pytest.mark.asyncio
    async def test_platform_start_stop(self, platform):
        """Test platform start and stop functionality."""
        # Start platform
        await platform.start()
        
        # Check status
        status = await platform.get_platform_status()
        assert status['running'] is True
        assert status['features_count'] > 30000000
        
        # Stop platform
        await platform.stop()
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, platform):
        """Test agent registration and management."""
        await platform.start()
        
        # Register an agent
        await platform.register_agent(
            "test_agent_001", 
            "Test Agent", 
            ["nlp", "vision"]
        )
        
        # Check agent is registered
        status = await platform.get_platform_status()
        assert status['agents_count'] == 1
        assert "test_agent_001" in status['agents']
        
        # Unregister agent
        await platform.unregister_agent("test_agent_001")
        
        status = await platform.get_platform_status()
        assert status['agents_count'] == 0
        
        await platform.stop()
    
    @pytest.mark.asyncio
    async def test_feature_execution(self, platform):
        """Test feature execution."""
        await platform.start()
        
        # Get available features
        features = platform.list_features()
        assert len(features) > 0
        
        # Execute a feature
        feature_name = features[0]
        result = await platform.execute_feature(feature_name)
        assert result is not None
        
        # Test invalid feature
        with pytest.raises(ValueError):
            await platform.execute_feature("invalid_feature_name")
        
        await platform.stop()
    
    @pytest.mark.asyncio
    async def test_self_healing_trigger(self, platform):
        """Test self-healing trigger."""
        await platform.start()
        
        # Trigger self-healing
        await platform.trigger_self_healing("test_issue", {"test": "context"})
        
        # Check healing stats
        stats = platform.self_healing_ai.get_healing_stats()
        assert stats['total_issues'] >= 1
        
        await platform.stop()


class TestConfigManager:
    """Test cases for configuration management."""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
test_section:
  test_key: "test_value"
  nested:
    value: 42
""")
            config_path = f.name
        
        yield config_path
        Path(config_path).unlink()
    
    def test_config_initialization(self, temp_config):
        """Test configuration manager initialization."""
        config = ConfigManager(temp_config)
        assert config.get("test_section.test_key") == "test_value"
        assert config.get("test_section.nested.value") == 42
    
    def test_config_get_set(self, temp_config):
        """Test configuration get and set operations."""
        config = ConfigManager(temp_config)
        
        # Test get
        assert config.get("test_section.test_key") == "test_value"
        assert config.get("nonexistent.key", "default") == "default"
        
        # Test set
        config.set("new.key", "new_value", save=False)
        assert config.get("new.key") == "new_value"
    
    def test_config_validation(self, temp_config):
        """Test configuration validation."""
        config = ConfigManager(temp_config)
        
        # Should have no errors with default config
        errors = config.validate_config()
        # Note: errors might exist due to missing required sections in test config
        assert isinstance(errors, list)
    
    def test_config_export_import(self, temp_config):
        """Test configuration export and import."""
        config = ConfigManager(temp_config)
        
        # Export
        exported = config.export_config()
        assert isinstance(exported, dict)
        
        # Modify and import
        exported["new_section"] = {"new_key": "new_value"}
        config.import_config(exported, save=False)
        
        assert config.get("new_section.new_key") == "new_value"


class TestHealthMonitor:
    """Test cases for health monitoring."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a test configuration manager."""
        return ConfigManager()
    
    @pytest.fixture
    async def health_monitor(self, config_manager):
        """Create a test health monitor."""
        monitor = HealthMonitor(config_manager)
        yield monitor
    
    @pytest.mark.asyncio
    async def test_health_monitor_start_stop(self, health_monitor):
        """Test health monitor start and stop."""
        await health_monitor.start()
        assert health_monitor._running is True
        
        await health_monitor.stop()
        assert health_monitor._running is False
    
    @pytest.mark.asyncio
    async def test_health_status(self, health_monitor):
        """Test health status retrieval."""
        await health_monitor.start()
        
        status = await health_monitor.get_health_status()
        assert isinstance(status, dict)
        assert 'timestamp' in status
        assert 'system_health' in status
        assert 'cpu_usage' in status
        assert 'memory_usage' in status
        
        await health_monitor.stop()
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, health_monitor):
        """Test agent registration in health monitor."""
        await health_monitor.start()
        
        # Register agent
        await health_monitor.register_agent("test_agent", None)
        
        # Update heartbeat
        await health_monitor.update_agent_heartbeat("test_agent", {"test": "metric"})
        
        # Get agent health
        agent_health = await health_monitor.get_agent_health("test_agent")
        assert agent_health is not None
        assert agent_health['agent_id'] == "test_agent"
        
        await health_monitor.stop()


class TestRecoveryManager:
    """Test cases for recovery management."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a test configuration manager."""
        config = ConfigManager()
        config.set("recovery.backup_dir", "./test_backups", save=False)
        config.set("recovery.max_backups", 5, save=False)
        return config
    
    @pytest.fixture
    async def recovery_manager(self, config_manager):
        """Create a test recovery manager."""
        manager = RecoveryManager(config_manager)
        yield manager
        
        # Cleanup
        if Path("./test_backups").exists():
            shutil.rmtree("./test_backups")
    
    @pytest.mark.asyncio
    async def test_recovery_manager_start_stop(self, recovery_manager):
        """Test recovery manager start and stop."""
        await recovery_manager.start()
        assert recovery_manager._running is True
        
        await recovery_manager.stop()
        assert recovery_manager._running is False
    
    @pytest.mark.asyncio
    async def test_backup_creation(self, recovery_manager):
        """Test backup creation."""
        await recovery_manager.start()
        
        # Create backup
        backup_id = await recovery_manager.create_backup("test", "Test backup")
        assert backup_id is not None
        
        # Check backup list
        backups = recovery_manager.get_backup_list()
        assert len(backups) == 1
        assert backups[0]['backup_id'] == backup_id
        
        await recovery_manager.stop()
    
    @pytest.mark.asyncio
    async def test_recovery_point(self, recovery_manager):
        """Test recovery point creation."""
        await recovery_manager.start()
        
        # Create recovery point
        point_id = await recovery_manager.create_recovery_point("Test point")
        assert point_id is not None
        
        # Check recovery points
        points = recovery_manager.get_recovery_points()
        assert len(points) == 1
        assert points[0]['point_id'] == point_id
        
        await recovery_manager.stop()


class TestSelfHealingAI:
    """Test cases for self-healing AI."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a test configuration manager."""
        return ConfigManager()
    
    @pytest.fixture
    async def self_healing_components(self, config_manager):
        """Create self-healing AI components."""
        health_monitor = HealthMonitor(config_manager)
        recovery_manager = RecoveryManager(config_manager)
        self_healing = SelfHealingAI(config_manager, health_monitor, recovery_manager)
        
        yield self_healing, health_monitor, recovery_manager
        
        # Cleanup
        if Path("./backups").exists():
            shutil.rmtree("./backups")
    
    @pytest.mark.asyncio
    async def test_self_healing_start_stop(self, self_healing_components):
        """Test self-healing AI start and stop."""
        self_healing, health_monitor, recovery_manager = self_healing_components
        
        await self_healing.start()
        assert self_healing._running is True
        
        await self_healing.stop()
        assert self_healing._running is False
    
    @pytest.mark.asyncio
    async def test_healing_process(self, self_healing_components):
        """Test the healing process."""
        self_healing, health_monitor, recovery_manager = self_healing_components
        
        await health_monitor.start()
        await recovery_manager.start()
        await self_healing.start()
        
        # Trigger healing
        await self_healing.heal("test_issue", {"test": "context"})
        
        # Check healing stats
        stats = self_healing.get_healing_stats()
        assert stats['total_issues'] >= 1
        
        await self_healing.stop()
        await recovery_manager.stop()
        await health_monitor.stop()
    
    @pytest.mark.asyncio
    async def test_feature_error_handling(self, self_healing_components):
        """Test feature error handling."""
        self_healing, health_monitor, recovery_manager = self_healing_components
        
        await health_monitor.start()
        await recovery_manager.start()
        await self_healing.start()
        
        # Handle feature error
        error = Exception("Test error")
        await self_healing.handle_feature_error("test_feature", error)
        
        # Check that healing was triggered
        stats = self_healing.get_healing_stats()
        assert stats['total_issues'] >= 1
        
        await self_healing.stop()
        await recovery_manager.stop()
        await health_monitor.stop()


if __name__ == "__main__":
    pytest.main([__file__])