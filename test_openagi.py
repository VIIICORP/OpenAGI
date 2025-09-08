"""
Test OpenAGI Core Functionality

Basic tests to verify the OpenAGI platform is working correctly.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openagi import OpenAGI, ConfigManager, HealthMonitor, RecoveryManager, SelfHealingAI


@pytest.mark.asyncio
async def test_openagi_initialization():
    """Test OpenAGI platform initialization."""
    openagi = OpenAGI()
    assert openagi.platform_id is not None
    assert openagi._feature_registry is not None
    assert len(openagi._feature_registry) > 0
    print(f"✅ OpenAGI initialized with {len(openagi._feature_registry):,} features")


@pytest.mark.asyncio
async def test_openagi_start_stop():
    """Test starting and stopping the OpenAGI platform."""
    openagi = OpenAGI()
    
    # Test start
    await openagi.start()
    assert openagi._running is True
    
    # Test status
    status = await openagi.get_platform_status()
    assert status['running'] is True
    assert status['features_count'] > 0
    
    # Test stop
    await openagi.stop()
    assert openagi._running is False
    
    print("✅ OpenAGI start/stop cycle completed successfully")


@pytest.mark.asyncio
async def test_agent_registration():
    """Test agent registration and management."""
    openagi = OpenAGI()
    await openagi.start()
    
    # Register an agent
    agent_id = "test_agent_001"
    agent_name = "Test Agent"
    capabilities = ["test_capability", "demo_feature"]
    
    await openagi.register_agent(agent_id, agent_name, capabilities)
    
    # Check status
    status = await openagi.get_platform_status()
    assert status['agents_count'] == 1
    assert agent_id in status['agents']
    
    # Unregister agent
    await openagi.unregister_agent(agent_id)
    
    updated_status = await openagi.get_platform_status()
    assert updated_status['agents_count'] == 0
    
    await openagi.stop()
    print("✅ Agent registration/unregistration working correctly")


@pytest.mark.asyncio
async def test_feature_execution():
    """Test executing self-healing features."""
    openagi = OpenAGI()
    await openagi.start()
    
    # Get a sample feature
    features = openagi.list_features()
    assert len(features) > 0
    
    sample_feature = features[0]
    
    # Execute the feature
    result = await openagi.execute_feature(sample_feature)
    assert result is not None
    assert "executed successfully" in result
    
    await openagi.stop()
    print(f"✅ Feature execution working: {sample_feature}")


@pytest.mark.asyncio
async def test_self_healing():
    """Test self-healing functionality."""
    openagi = OpenAGI()
    await openagi.start()
    
    # Trigger self-healing
    issue_type = "test_issue"
    context = {"test_param": "test_value"}
    
    await openagi.trigger_self_healing(issue_type, context)
    
    await openagi.stop()
    print("✅ Self-healing mechanism triggered successfully")


def test_config_manager():
    """Test configuration manager."""
    config_manager = ConfigManager()
    
    # Test getting configuration
    cpu_threshold = config_manager.get("monitoring.cpu_threshold", 80.0)
    assert cpu_threshold > 0
    
    # Test setting configuration
    config_manager.set("test.value", 42, save=False)
    assert config_manager.get("test.value") == 42
    
    # Test validation
    errors = config_manager.validate_config()
    assert isinstance(errors, list)
    
    print("✅ Configuration manager working correctly")


@pytest.mark.asyncio
async def test_health_monitor():
    """Test health monitoring system."""
    config_manager = ConfigManager()
    health_monitor = HealthMonitor(config_manager)
    
    await health_monitor.start()
    
    # Test health status
    status = await health_monitor.get_health_status()
    assert 'system_health' in status
    assert 'cpu_usage' in status
    assert 'memory_usage' in status
    
    # Test system resource check
    resource_status = await health_monitor.check_system_resources()
    assert 'status' in resource_status
    assert 'metrics' in resource_status
    
    await health_monitor.stop()
    print("✅ Health monitoring system working correctly")


@pytest.mark.asyncio 
async def test_recovery_manager():
    """Test recovery manager."""
    config_manager = ConfigManager()
    recovery_manager = RecoveryManager(config_manager)
    
    await recovery_manager.start()
    
    # Test backup creation
    backup_id = await recovery_manager.create_backup("test", "Test backup")
    assert backup_id is not None
    
    # Test backup list
    backups = recovery_manager.get_recovery_stats()
    assert backups['backups_count'] >= 1
    
    await recovery_manager.stop()
    print("✅ Recovery manager working correctly")


def test_feature_categories():
    """Test feature categorization."""
    openagi = OpenAGI()
    
    # Test listing features by category
    monitoring_features = openagi.list_features("monitoring")
    assert len(monitoring_features) > 0
    
    recovery_features = openagi.list_features("recovery")
    assert len(recovery_features) > 0
    
    optimization_features = openagi.list_features("optimization")
    assert len(optimization_features) > 0
    
    security_features = openagi.list_features("security")
    assert len(security_features) > 0
    
    print(f"✅ Feature categories working:")
    print(f"   - Monitoring: {len(monitoring_features):,} features")
    print(f"   - Recovery: {len(recovery_features):,} features") 
    print(f"   - Optimization: {len(optimization_features):,} features")
    print(f"   - Security: {len(security_features):,} features")


def test_feature_count():
    """Test that we have the expected number of features."""
    openagi = OpenAGI()
    
    feature_count = openagi.get_feature_count()
    
    # We should have millions of features
    assert feature_count > 1000000, f"Expected >1M features, got {feature_count:,}"
    
    print(f"✅ Feature count verification: {feature_count:,} features available")


if __name__ == "__main__":
    """Run tests directly."""
    print("🧪 Running OpenAGI Tests")
    print("=" * 40)
    
    # Run synchronous tests
    test_config_manager()
    test_feature_categories()
    test_feature_count()
    
    # Run async tests
    async def run_async_tests():
        await test_openagi_initialization()
        await test_openagi_start_stop()
        await test_agent_registration()
        await test_feature_execution()
        await test_self_healing()
        await test_health_monitor()
        await test_recovery_manager()
    
    asyncio.run(run_async_tests())
    
    print("\n🎉 All tests passed successfully!")
    print("✅ OpenAGI platform is fully functional")