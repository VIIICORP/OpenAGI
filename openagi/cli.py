"""Command-line interface for OpenAGI platform."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from openagi.core.config import OpenAGIConfig
from openagi.core.platform import OpenAGIPlatform
from openagi.core.logger import get_openagi_logger


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="OpenAGI - Comprehensive AI Platform with Self-Debugging Features"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="API server host (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--no-debug-engine",
        action="store_true",
        help="Disable debug engine"
    )
    
    parser.add_argument(
        "--no-monitoring",
        action="store_true",
        help="Disable monitoring system"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )
    
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data"),
        help="Data directory (default: ./data)"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command (default)
    run_parser = subparsers.add_parser("run", help="Run the OpenAGI platform")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check platform status")
    status_parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Platform API URL"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    # Generate default config
    generate_parser = config_subparsers.add_parser("generate", help="Generate default configuration")
    generate_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("openagi_config.yaml"),
        help="Output configuration file"
    )
    
    # Validate config
    validate_parser = config_subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument(
        "config_file",
        type=Path,
        help="Configuration file to validate"
    )
    
    return parser


async def run_platform(args: argparse.Namespace) -> None:
    """Run the OpenAGI platform."""
    try:
        # Load configuration
        if args.config:
            config = OpenAGIConfig.from_file(args.config)
        else:
            config = OpenAGIConfig()
        
        # Override config with CLI arguments
        if args.host:
            config.api.host = args.host
        if args.port:
            config.api.port = args.port
        if args.debug:
            config.api.debug = True
            config.monitoring.log_level = "DEBUG"
        if args.no_debug_engine:
            config.debugging.enable_auto_debug = False
        if args.no_monitoring:
            config.monitoring.enable_metrics = False
        if args.log_level:
            config.monitoring.log_level = args.log_level
        if args.log_file:
            config.monitoring.log_file = args.log_file
        if args.data_dir:
            config.data_dir = args.data_dir
        
        # Create and run platform
        platform = OpenAGIPlatform(config)
        await platform.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error running platform: {e}")
        sys.exit(1)


async def check_status(args: argparse.Namespace) -> None:
    """Check platform status."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{args.url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Platform Status: {data['status']}")
                    print(f"Version: {data['version']}")
                    print(f"Uptime: {data['uptime_seconds']:.1f} seconds")
                    print("\nComponents:")
                    for name, status in data['components'].items():
                        healthy = status.get('healthy', False)
                        print(f"  {name}: {'✓' if healthy else '✗'}")
                else:
                    print(f"Error: HTTP {response.status}")
                    
    except aiohttp.ClientError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error checking status: {e}")


def generate_config(args: argparse.Namespace) -> None:
    """Generate default configuration file."""
    try:
        config = OpenAGIConfig()
        config.save_to_file(args.output)
        print(f"Default configuration saved to: {args.output}")
        
    except Exception as e:
        print(f"Error generating config: {e}")
        sys.exit(1)


def validate_config(args: argparse.Namespace) -> None:
    """Validate configuration file."""
    try:
        config = OpenAGIConfig.from_file(args.config_file)
        print(f"Configuration file '{args.config_file}' is valid")
        print(f"App Name: {config.app_name}")
        print(f"Version: {config.app_version}")
        print(f"Environment: {config.environment}")
        
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error validating config: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Default to run command if no command specified
    if not args.command:
        args.command = "run"
    
    if args.command == "run":
        asyncio.run(run_platform(args))
    elif args.command == "status":
        asyncio.run(check_status(args))
    elif args.command == "config":
        if args.config_action == "generate":
            generate_config(args)
        elif args.config_action == "validate":
            validate_config(args)
        else:
            parser.error("Config command requires an action (generate or validate)")
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()