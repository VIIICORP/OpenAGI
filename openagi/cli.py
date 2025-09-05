"""
OpenAGI Command Line Interface

This module provides a comprehensive CLI for managing the OpenAGI platform.
"""

import asyncio
import click
import json
import sys
import time
from typing import Optional
import logging

from . import OpenAGI
from .config import ConfigManager


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """OpenAGI - Comprehensive AI platform with 30M+ Self Healing features."""
    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store context
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose


@cli.command()
@click.pass_context
def start(ctx):
    """Start the OpenAGI platform."""
    config_path = ctx.obj.get('config_path')
    
    async def _start():
        openagi = OpenAGI(config_path)
        try:
            click.echo("Starting OpenAGI platform...")
            await openagi.start()
            
            # Display startup information
            status = await openagi.get_platform_status()
            click.echo(f"✅ Platform started successfully!")
            click.echo(f"📊 Platform ID: {status['platform_id']}")
            click.echo(f"🔧 Features available: {status['features_count']:,}")
            click.echo(f"👥 Agents registered: {status['agents_count']}")
            
            # Keep running until interrupted
            click.echo("Press Ctrl+C to stop...")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping platform...")
                await openagi.stop()
                click.echo("✅ Platform stopped successfully!")
                
        except Exception as e:
            click.echo(f"❌ Error starting platform: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_start())


@cli.command()
@click.pass_context
def status(ctx):
    """Get platform status."""
    config_path = ctx.obj.get('config_path')
    
    async def _status():
        openagi = OpenAGI(config_path)
        try:
            await openagi.start()
            status = await openagi.get_platform_status()
            await openagi.stop()
            
            click.echo("📊 OpenAGI Platform Status")
            click.echo("=" * 40)
            click.echo(f"Platform ID: {status['platform_id']}")
            click.echo(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
            click.echo(f"Uptime: {status['uptime']:.1f} seconds")
            click.echo(f"Features: {status['features_count']:,}")
            click.echo(f"Agents: {status['agents_count']}")
            click.echo(f"Health: {status['health_status'].get('system_health', 'Unknown')}")
            
            if ctx.obj.get('verbose'):
                click.echo(f"\n📈 Detailed Metrics:")
                health = status['health_status']
                click.echo(f"  CPU Usage: {health.get('cpu_usage', 0):.1f}%")
                click.echo(f"  Memory Usage: {health.get('memory_usage', 0):.1f}%")
                click.echo(f"  Disk Usage: {health.get('disk_usage', 0):.1f}%")
                
        except Exception as e:
            click.echo(f"❌ Error getting status: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_status())


@cli.command()
@click.option('--feature', '-f', help='Specific feature to execute')
@click.option('--list-features', '-l', is_flag=True, help='List available features')
@click.option('--category', '-c', help='Filter features by category')
@click.pass_context
def features(ctx, feature: Optional[str], list_features: bool, category: Optional[str]):
    """Manage and execute platform features."""
    config_path = ctx.obj.get('config_path')
    
    async def _features():
        openagi = OpenAGI(config_path)
        try:
            await openagi.start()
            
            if list_features:
                features_list = openagi.list_features(category)
                total_features = openagi.get_feature_count()
                
                click.echo(f"🔧 Available Features: {total_features:,} total")
                if category:
                    click.echo(f"📂 Category: {category} ({len(features_list)} features)")
                
                if len(features_list) > 20:
                    click.echo("📝 Showing first 20 features (use --category to filter):")
                    features_list = features_list[:20]
                
                for feat in features_list:
                    click.echo(f"  • {feat}")
                
                if total_features > 20 and not category:
                    click.echo(f"... and {total_features - 20:,} more features")
            
            elif feature:
                click.echo(f"🚀 Executing feature: {feature}")
                try:
                    result = await openagi.execute_feature(feature)
                    click.echo(f"✅ Result: {result}")
                except ValueError as e:
                    click.echo(f"❌ {e}", err=True)
                    sys.exit(1)
            else:
                click.echo("Use --list-features to see available features or --feature to execute one")
            
            await openagi.stop()
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_features())


@cli.command()
@click.option('--agent-id', required=True, help='Agent ID to register')
@click.option('--name', required=True, help='Agent name')
@click.option('--capabilities', help='Comma-separated list of capabilities')
@click.pass_context
def register_agent(ctx, agent_id: str, name: str, capabilities: Optional[str]):
    """Register a new AI agent."""
    config_path = ctx.obj.get('config_path')
    caps = capabilities.split(',') if capabilities else []
    
    async def _register():
        openagi = OpenAGI(config_path)
        try:
            await openagi.start()
            await openagi.register_agent(agent_id, name, caps)
            click.echo(f"✅ Agent registered: {name} ({agent_id})")
            click.echo(f"🔧 Capabilities: {', '.join(caps) if caps else 'None'}")
            await openagi.stop()
            
        except Exception as e:
            click.echo(f"❌ Error registering agent: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_register())


@cli.command()
@click.option('--issue-type', required=True, help='Type of issue to heal')
@click.option('--context', help='JSON context for the healing process')
@click.pass_context
def heal(ctx, issue_type: str, context: Optional[str]):
    """Trigger self-healing for a specific issue."""
    config_path = ctx.obj.get('config_path')
    
    try:
        context_dict = json.loads(context) if context else {}
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON context", err=True)
        sys.exit(1)
    
    async def _heal():
        openagi = OpenAGI(config_path)
        try:
            await openagi.start()
            click.echo(f"🔄 Triggering self-healing for: {issue_type}")
            await openagi.trigger_self_healing(issue_type, context_dict)
            click.echo("✅ Self-healing process initiated")
            await openagi.stop()
            
        except Exception as e:
            click.echo(f"❌ Error triggering healing: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_heal())


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.option('--key', required=True, help='Configuration key')
@click.option('--config-file', '-c', help='Configuration file path')
def get(key: str, config_file: Optional[str]):
    """Get configuration value."""
    try:
        config_manager = ConfigManager(config_file)
        value = config_manager.get(key)
        
        if value is not None:
            if isinstance(value, (dict, list)):
                click.echo(json.dumps(value, indent=2))
            else:
                click.echo(str(value))
        else:
            click.echo(f"❌ Configuration key not found: {key}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error getting configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option('--key', required=True, help='Configuration key')
@click.option('--value', required=True, help='Configuration value (JSON format)')
@click.option('--config-file', '-c', help='Configuration file path')
def set(key: str, value: str, config_file: Optional[str]):
    """Set configuration value."""
    try:
        # Try to parse as JSON, fallback to string
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        config_manager = ConfigManager(config_file)
        config_manager.set(key, parsed_value)
        click.echo(f"✅ Configuration updated: {key} = {parsed_value}")
        
    except Exception as e:
        click.echo(f"❌ Error setting configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option('--config-file', '-c', help='Configuration file path')
def validate(config_file: Optional[str]):
    """Validate configuration."""
    try:
        config_manager = ConfigManager(config_file)
        errors = config_manager.validate_config()
        
        if not errors:
            click.echo("✅ Configuration is valid")
        else:
            click.echo("❌ Configuration validation errors:")
            for error in errors:
                click.echo(f"  • {error}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error validating configuration: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option('--config-file', '-c', help='Configuration file path')
def info(config_file: Optional[str]):
    """Show configuration information."""
    try:
        config_manager = ConfigManager(config_file)
        info = config_manager.get_config_info()
        
        click.echo("📋 Configuration Information")
        click.echo("=" * 40)
        click.echo(f"File: {info['config_file']}")
        click.echo(f"Exists: {'✅ Yes' if info['config_exists'] else '❌ No'}")
        click.echo(f"Size: {info['config_size_bytes']} bytes")
        click.echo(f"History Versions: {info['history_versions']}")
        
        if info['last_modified']:
            modified_time = time.ctime(info['last_modified'])
            click.echo(f"Last Modified: {modified_time}")
        
        errors = info['validation_errors']
        if errors:
            click.echo(f"\n❌ Validation Errors ({len(errors)}):")
            for error in errors:
                click.echo(f"  • {error}")
        else:
            click.echo("\n✅ No validation errors")
            
    except Exception as e:
        click.echo(f"❌ Error getting configuration info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__
    
    click.echo(f"OpenAGI Platform v{__version__}")
    click.echo("Comprehensive AI platform with 30M+ Self Healing features")
    click.echo("Copyright (c) 2024 VIIICORP")


@cli.command()
@click.option('--check-system', is_flag=True, help='Check system requirements')
@click.pass_context
def doctor(ctx, check_system: bool):
    """Diagnose platform health and configuration."""
    config_path = ctx.obj.get('config_path')
    
    click.echo("🏥 OpenAGI Health Check")
    click.echo("=" * 40)
    
    # Check configuration
    try:
        config_manager = ConfigManager(config_path)
        errors = config_manager.validate_config()
        
        if not errors:
            click.echo("✅ Configuration: Valid")
        else:
            click.echo("❌ Configuration: Issues found")
            for error in errors:
                click.echo(f"  • {error}")
    except Exception as e:
        click.echo(f"❌ Configuration: Error - {e}")
    
    # Check system requirements
    if check_system:
        click.echo("\n🔍 System Requirements:")
        
        try:
            import sys
            click.echo(f"✅ Python: {sys.version.split()[0]}")
        except Exception:
            click.echo("❌ Python: Not available")
        
        required_packages = [
            'numpy', 'pandas', 'scikit-learn', 'torch', 
            'transformers', 'psutil', 'pyyaml', 'fastapi'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                click.echo(f"✅ {package}: Available")
            except ImportError:
                click.echo(f"❌ {package}: Missing")
    
    # Test platform initialization
    async def _test_init():
        try:
            openagi = OpenAGI(config_path)
            await openagi.start()
            status = await openagi.get_platform_status()
            await openagi.stop()
            
            click.echo("✅ Platform: Can initialize")
            click.echo(f"  Features: {status['features_count']:,}")
            
        except Exception as e:
            click.echo(f"❌ Platform: Initialization failed - {e}")
    
    asyncio.run(_test_init())


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()