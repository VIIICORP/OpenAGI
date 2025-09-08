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
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__
    
    click.echo(f"OpenAGI Platform v{__version__}")
    click.echo("Comprehensive AI platform with 30M+ Self Healing features")
    click.echo("Copyright (c) 2024 VIIICORP")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()