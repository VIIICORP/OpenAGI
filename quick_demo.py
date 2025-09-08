"""
Quick demo of OpenAGI functionality.
"""

import asyncio
import sys
from openagi import OpenAGI

async def demo_openagi():
    """Demonstrate OpenAGI platform capabilities."""
    print("🚀 OpenAGI Platform Demo")
    print("=" * 40)
    
    print("1. Initializing OpenAGI Platform...")
    openagi = OpenAGI()
    await openagi.start()
    
    status = await openagi.get_platform_status()
    print(f"   ✅ Platform initialized")
    print(f"   🤖 Agents: {status['agents_count']}")
    print(f"   🔌 Features: {status['features_count']:,}")
    print(f"   📊 Platform ID: {status['platform_id']}")
    
    print("\n2. Registering AI Agents...")
    
    # Register different types of agents
    await openagi.register_agent(
        agent_id="nlp_agent_001",
        name="Natural Language Processor",
        capabilities=["natural_language", "text_analysis", "sentiment_analysis"]
    )
    
    await openagi.register_agent(
        agent_id="vision_agent_001", 
        name="Computer Vision Specialist",
        capabilities=["computer_vision", "image_analysis", "object_detection"]
    )
    
    await openagi.register_agent(
        agent_id="reasoning_agent_001",
        name="Logical Reasoning Engine", 
        capabilities=["reasoning", "problem_solving", "decision_making"]
    )
    
    print(f"   ✅ Registered 3 AI agents")
    
    print("\n3. Executing Self-Healing Features...")
    
    # Execute various self-healing features
    features_to_test = [
        "monitoring_health_check_advanced_realtime",
        "optimization_performance_tuning_neural_autonomous",
        "security_threat_detection_premium_streaming",
        "learning_adaptive_learning_quantum_meta",
        "recovery_backup_recovery_enterprise_automated"
    ]
    
    for i, feature in enumerate(features_to_test, 1):
        try:
            result = await openagi.execute_feature(feature)
            print(f"   ✅ Feature {i}/5: {feature[:30]}... executed")
        except Exception as e:
            print(f"   ⚠️  Feature {i}/5: Error - {str(e)[:50]}...")
    
    print("\n4. Testing Self-Healing Capabilities...")
    
    # Trigger self-healing scenarios
    healing_scenarios = [
        ("high_cpu_usage", {"cpu_usage": 85.5}),
        ("agent_unhealthy", {"agent_id": "nlp_agent_001", "last_response": 120}),
        ("network_error", {"error_type": "connection_timeout", "component": "api_gateway"}),
        ("memory_leak", {"memory_usage": 92.1, "process": "learning_engine"})
    ]
    
    for scenario, context in healing_scenarios:
        await openagi.trigger_self_healing(scenario, context)
        print(f"   🔄 Self-healing triggered for: {scenario}")
    
    print("\n5. Platform Statistics...")
    
    updated_status = await openagi.get_platform_status()
    health_status = updated_status['health_status']
    
    print(f"   📈 CPU Usage: {health_status.get('cpu_usage', 0):.1f}%")
    print(f"   💾 Memory Usage: {health_status.get('memory_usage', 0):.1f}%")
    print(f"   💿 Disk Usage: {health_status.get('disk_usage', 0):.1f}%")
    print(f"   ⏱️  Uptime: {updated_status['uptime']:.1f} seconds")
    print(f"   🎯 System Health: {health_status.get('system_health', 'Unknown')}")
    
    print("\n6. Feature Categories...")
    
    # Show feature categories
    categories = [
        "monitoring", "recovery", "optimization", "security", 
        "learning", "prediction", "adaptation", "validation"
    ]
    
    for category in categories:
        category_features = openagi.list_features(category)
        print(f"   📂 {category.title()}: {len(category_features):,} features")
    
    print("\n7. Shutting Down...")
    await openagi.stop()
    
    print("\n✅ Demo completed successfully!")
    print("🎉 OpenAGI Platform with 30M+ self-healing capabilities demonstrated!")
    print("\n💡 Next steps:")
    print("   - Try: openagi start")
    print("   - Try: openagi status")
    print("   - Try: openagi features --list-features")
    print("   - Try: openagi heal --issue-type high_cpu_usage --context '{\"cpu_usage\": 85}'")

if __name__ == "__main__":
    try:
        asyncio.run(demo_openagi())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)