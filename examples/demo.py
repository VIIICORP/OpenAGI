#!/usr/bin/env python3
"""
OpenAGI Platform Demo

This script demonstrates the key capabilities of the OpenAGI platform
with 30M+ self-healing AI features.
"""

import asyncio
import json
import time
from openagi import OpenAGI


async def demo_basic_platform():
    """Demonstrate basic platform functionality."""
    print("🚀 OpenAGI Platform Demo")
    print("=" * 50)
    
    # Initialize platform
    print("📦 Initializing OpenAGI platform...")
    platform = OpenAGI()
    
    # Start platform
    print("🔄 Starting platform...")
    await platform.start()
    
    # Show platform status
    status = await platform.get_platform_status()
    print(f"✅ Platform started successfully!")
    print(f"   Platform ID: {status['platform_id']}")
    print(f"   Features available: {status['features_count']:,}")
    print(f"   System health: {status['health_status'].get('system_health', 'Unknown')}")
    
    return platform


async def demo_agent_management(platform):
    """Demonstrate AI agent management."""
    print("\n👥 AI Agent Management Demo")
    print("-" * 30)
    
    # Register multiple agents
    agents = [
        ("agent_nlp_001", "Natural Language Processor", ["nlp", "text_analysis", "translation"]),
        ("agent_vision_001", "Computer Vision Agent", ["image_recognition", "object_detection", "ocr"]),
        ("agent_reasoning_001", "Reasoning Engine", ["logic", "inference", "decision_making"]),
    ]
    
    for agent_id, name, capabilities in agents:
        await platform.register_agent(agent_id, name, capabilities)
        print(f"   ✅ Registered: {name} ({agent_id})")
    
    # Show updated status
    status = await platform.get_platform_status()
    print(f"   📊 Total agents: {status['agents_count']}")


async def demo_self_healing_features(platform):
    """Demonstrate self-healing capabilities."""
    print("\n🔧 Self-Healing Features Demo")
    print("-" * 30)
    
    # Show feature categories
    categories = ["monitoring", "recovery", "optimization", "security"]
    
    for category in categories:
        features = platform.list_features(category)
        print(f"   📂 {category.title()}: {len(features):,} features")
        
        # Show a few example features
        for feature in features[:3]:
            print(f"      • {feature}")
        if len(features) > 3:
            print(f"      ... and {len(features) - 3:,} more")
    
    # Execute some sample features
    print("\n   🚀 Executing sample features:")
    sample_features = [
        "monitoring_health_check_basic_realtime",
        "optimization_performance_tuning_advanced_batch",
        "security_threat_detection_premium_streaming"
    ]
    
    for feature in sample_features:
        try:
            result = await platform.execute_feature(feature)
            print(f"      ✅ {feature}: {result}")
        except Exception as e:
            print(f"      ❌ {feature}: {e}")


async def demo_monitoring_system(platform):
    """Demonstrate monitoring capabilities."""
    print("\n📊 Health Monitoring Demo")
    print("-" * 30)
    
    # Get current health status
    health = await platform.get_platform_status()
    health_info = health['health_status']
    
    print(f"   🖥️  System Health: {health_info.get('system_health', 'Unknown')}")
    print(f"   ⚡ CPU Usage: {health_info.get('cpu_usage', 0):.1f}%")
    print(f"   💾 Memory Usage: {health_info.get('memory_usage', 0):.1f}%")
    print(f"   💿 Disk Usage: {health_info.get('disk_usage', 0):.1f}%")
    print(f"   🔄 Processes: {health_info.get('process_count', 0)}")
    print(f"   📡 Uptime: {health_info.get('uptime', 0):.1f} seconds")
    
    # Show agent health
    agents_info = health_info.get('agents', {})
    print(f"   👥 Agent Health: {agents_info.get('healthy', 0)}/{agents_info.get('total', 0)} healthy")


async def demo_self_healing_trigger(platform):
    """Demonstrate self-healing in action."""
    print("\n🔄 Self-Healing Demo")
    print("-" * 30)
    
    # Simulate various issues and trigger healing
    test_issues = [
        ("high_cpu_usage", {"cpu_usage": 85, "component": "agent_nlp_001"}),
        ("agent_unhealthy", {"agent_id": "agent_vision_001", "last_response": 120}),
        ("memory_leak", {"memory_usage": 90, "component": "reasoning_engine"}),
        ("network_timeout", {"timeout_duration": 30, "target": "external_api"}),
    ]
    
    for issue_type, context in test_issues:
        print(f"   🚨 Simulating issue: {issue_type}")
        await platform.trigger_self_healing(issue_type, context)
        print(f"   ✅ Self-healing triggered for: {issue_type}")
        await asyncio.sleep(1)  # Small delay for demonstration
    
    # Show healing statistics
    healing_stats = platform.self_healing_ai.get_healing_stats()
    print(f"\n   📈 Healing Statistics:")
    print(f"      Issues detected: {healing_stats['total_issues']}")
    print(f"      Issues resolved: {healing_stats['resolved_issues']}")
    print(f"      Healing actions: {healing_stats['total_healing_actions']}")
    print(f"      Success rate: {healing_stats['success_rate']:.1f}%")


async def demo_backup_recovery(platform):
    """Demonstrate backup and recovery capabilities."""
    print("\n💾 Backup & Recovery Demo")
    print("-" * 30)
    
    # Create a backup
    print("   📦 Creating platform backup...")
    backup_id = await platform.recovery_manager.create_backup(
        "demo", "Demo backup for testing"
    )
    print(f"   ✅ Backup created: {backup_id}")
    
    # Create a recovery point
    print("   📍 Creating recovery point...")
    point_id = await platform.recovery_manager.create_recovery_point(
        "Demo recovery point"
    )
    print(f"   ✅ Recovery point created: {point_id}")
    
    # Show backup statistics
    recovery_stats = platform.recovery_manager.get_recovery_stats()
    print(f"\n   📊 Recovery Statistics:")
    print(f"      Backups: {recovery_stats['backups_count']}")
    print(f"      Recovery points: {recovery_stats['recovery_points_count']}")
    print(f"      Total backup size: {recovery_stats['total_backup_size_bytes']} bytes")


async def demo_configuration_management(platform):
    """Demonstrate configuration management."""
    print("\n⚙️  Configuration Management Demo")
    print("-" * 30)
    
    config = platform.config_manager
    
    # Show current configuration
    cpu_threshold = config.get("monitoring.cpu_threshold")
    memory_threshold = config.get("monitoring.memory_threshold")
    max_agents = config.get("platform.max_agents")
    
    print(f"   📊 Current Settings:")
    print(f"      CPU Threshold: {cpu_threshold}%")
    print(f"      Memory Threshold: {memory_threshold}%")
    print(f"      Max Agents: {max_agents}")
    
    # Demonstrate dynamic configuration update
    print("\n   🔄 Updating configuration dynamically...")
    config.set("monitoring.cpu_threshold", 75, save=False)
    config.set("platform.max_agents", 2000, save=False)
    
    new_cpu_threshold = config.get("monitoring.cpu_threshold")
    new_max_agents = config.get("platform.max_agents")
    
    print(f"   ✅ Updated CPU Threshold: {new_cpu_threshold}%")
    print(f"   ✅ Updated Max Agents: {new_max_agents}")
    
    # Validate configuration
    errors = config.validate_config()
    if not errors:
        print("   ✅ Configuration is valid")
    else:
        print(f"   ⚠️  Configuration issues: {len(errors)}")


async def demo_performance_stats(platform):
    """Show platform performance statistics."""
    print("\n📈 Performance Statistics")
    print("-" * 30)
    
    status = await platform.get_platform_status()
    monitoring_stats = platform.health_monitor.get_monitoring_stats()
    
    print(f"   🎯 Platform Performance:")
    print(f"      Feature count: {status['features_count']:,}")
    print(f"      Active agents: {status['agents_count']}")
    print(f"      Uptime: {monitoring_stats['uptime']:.1f} seconds")
    print(f"      Metrics collected: {monitoring_stats['metrics_collected']}")
    print(f"      Alerts generated: {monitoring_stats['alerts_generated']}")
    print(f"      Monitoring status: {monitoring_stats['monitoring_status']}")


async def main():
    """Main demo function."""
    try:
        # Initialize and start platform
        platform = await demo_basic_platform()
        
        # Wait a moment for systems to initialize
        await asyncio.sleep(2)
        
        # Run demonstration modules
        await demo_agent_management(platform)
        await demo_self_healing_features(platform)
        await demo_monitoring_system(platform)
        await demo_self_healing_trigger(platform)
        await demo_backup_recovery(platform)
        await demo_configuration_management(platform)
        await demo_performance_stats(platform)
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("OpenAGI platform successfully demonstrated all major capabilities:")
        print("✅ 30M+ self-healing AI features")
        print("✅ Autonomous agent management")
        print("✅ Real-time health monitoring")
        print("✅ Intelligent recovery systems")
        print("✅ Dynamic configuration management")
        print("✅ Comprehensive backup & recovery")
        
        # Stop platform
        print("\n🛑 Stopping platform...")
        await platform.stop()
        print("✅ Platform stopped successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        if 'platform' in locals():
            await platform.stop()
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        if 'platform' in locals():
            await platform.stop()


if __name__ == "__main__":
    print("Starting OpenAGI Platform Demo...")
    asyncio.run(main())