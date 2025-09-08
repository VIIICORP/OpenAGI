"""
Simple verification test for OpenAGI platform without external dependencies.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from openagi import OpenAGI, ConfigManager
    print("✅ Successfully imported OpenAGI modules")
except ImportError as e:
    print(f"❌ Failed to import OpenAGI modules: {e}")
    sys.exit(1)


async def test_basic_functionality():
    """Test basic OpenAGI functionality."""
    print("\n🧪 Testing OpenAGI Basic Functionality")
    print("=" * 40)
    
    try:
        # Test 1: Initialization
        print("1. Testing initialization...")
        openagi = OpenAGI()
        print(f"   ✅ Platform ID: {openagi.platform_id}")
        print(f"   ✅ Features: {openagi.get_feature_count():,}")
        
        # Test 2: Configuration
        print("\n2. Testing configuration...")
        config_manager = ConfigManager()
        cpu_threshold = config_manager.get("monitoring.cpu_threshold", 80.0)
        print(f"   ✅ CPU threshold: {cpu_threshold}%")
        
        # Test 3: Feature listing
        print("\n3. Testing feature categories...")
        monitoring_features = openagi.list_features("monitoring")
        recovery_features = openagi.list_features("recovery")
        print(f"   ✅ Monitoring features: {len(monitoring_features):,}")
        print(f"   ✅ Recovery features: {len(recovery_features):,}")
        
        # Test 4: Platform start/stop
        print("\n4. Testing platform lifecycle...")
        await openagi.start()
        print("   ✅ Platform started")
        
        status = await openagi.get_platform_status()
        print(f"   ✅ Platform running: {status['running']}")
        print(f"   ✅ Features available: {status['features_count']:,}")
        
        # Test 5: Agent registration
        print("\n5. Testing agent registration...")
        await openagi.register_agent(
            agent_id="test_agent",
            name="Test Agent",
            capabilities=["test"]
        )
        
        updated_status = await openagi.get_platform_status()
        print(f"   ✅ Agents registered: {updated_status['agents_count']}")
        
        # Test 6: Feature execution
        print("\n6. Testing feature execution...")
        features = openagi.list_features()
        if features:
            sample_feature = features[0]
            result = await openagi.execute_feature(sample_feature)
            print(f"   ✅ Feature executed: {sample_feature[:50]}...")
        
        # Test 7: Self-healing
        print("\n7. Testing self-healing...")
        await openagi.trigger_self_healing("test_issue", {"test": "value"})
        print("   ✅ Self-healing triggered")
        
        # Cleanup
        await openagi.stop()
        print("\n   ✅ Platform stopped")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run verification tests."""
    print("🚀 OpenAGI Platform Verification")
    print("=" * 40)
    
    # Run async tests
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("\n🎉 All verification tests passed!")
        print("✅ OpenAGI platform is fully functional")
        print("\n💡 Next steps:")
        print("   - Run: python quick_demo.py")
        print("   - Try: python -c 'from openagi import OpenAGI; print(\"OpenAGI imported successfully!\")'")
        return 0
    else:
        print("\n❌ Verification tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())