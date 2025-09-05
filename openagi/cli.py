"""Command Line Interface for OpenAGI platform."""

import asyncio
import click
import json
import yaml
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from .core.engine import OpenAGIEngine
from .api.server import run_server
from .config.settings import Config


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", type=str, help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """OpenAGI - Comprehensive AI Platform with 30M+ Self-Learning Features."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind the server")
@click.option("--port", "-p", default=8000, help="Port to bind the server")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def serve(ctx, host: str, port: int, reload: bool):
    """Start the OpenAGI API server."""
    click.echo(f"🚀 Starting OpenAGI Server on {host}:{port}")
    
    try:
        run_server(
            config_path=ctx.obj.get("config_path"),
            host=host,
            port=port,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
    except Exception as e:
        click.echo(f"❌ Server failed to start: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.pass_context
def execute(ctx, task_file: str, output: Optional[str]):
    """Execute a task from a JSON/YAML file."""
    click.echo(f"📋 Executing task from {task_file}")
    
    try:
        # Load task data
        task_path = Path(task_file)
        with open(task_path, 'r') as f:
            if task_path.suffix.lower() in ['.yaml', '.yml']:
                task_data = yaml.safe_load(f)
            else:
                task_data = json.load(f)
        
        # Execute task
        result = asyncio.run(_execute_task(ctx.obj.get("config_path"), task_data))
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"✅ Results saved to {output}")
        else:
            click.echo("📊 Results:")
            click.echo(json.dumps(result, indent=2))
            
    except Exception as e:
        click.echo(f"❌ Task execution failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--algorithm", "-a", default="neural_network", help="Learning algorithm")
@click.option("--epochs", "-e", default=100, help="Number of training epochs")
@click.pass_context
def learn(ctx, data_file: str, algorithm: str, epochs: int):
    """Train the AI system with data from a file."""
    click.echo(f"🧠 Training with data from {data_file}")
    
    try:
        # Load training data
        with open(data_file, 'r') as f:
            if data_file.endswith('.json'):
                training_data = json.load(f)
            else:
                training_data = yaml.safe_load(f)
        
        # Execute learning
        result = asyncio.run(_execute_learning(
            ctx.obj.get("config_path"), 
            training_data, 
            algorithm, 
            epochs
        ))
        
        click.echo(f"✅ Training completed:")
        click.echo(f"   Algorithm: {algorithm}")
        click.echo(f"   Epochs: {epochs}")
        click.echo(f"   Final Performance: {result.get('final_performance', 'N/A')}")
        
    except Exception as e:
        click.echo(f"❌ Learning failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and statistics."""
    click.echo("📊 OpenAGI System Status")
    
    try:
        status_info = asyncio.run(_get_system_status(ctx.obj.get("config_path")))
        
        click.echo(f"🔧 Engine Status: {status_info['status']}")
        click.echo(f"⏱️  Uptime: {status_info['uptime_seconds']:.1f} seconds")
        click.echo(f"🤖 Agents: {len(status_info['agents'])}")
        click.echo(f"🔌 Plugins: {len(status_info['plugins'])}")
        click.echo(f"📈 Tasks Completed: {status_info['metrics']['tasks_completed']}")
        click.echo(f"🧠 Learning Iterations: {status_info['metrics']['learning_iterations']}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def evolve(ctx):
    """Trigger system evolution and improvement."""
    click.echo("🧬 Triggering system evolution...")
    
    try:
        result = asyncio.run(_trigger_evolution(ctx.obj.get("config_path")))
        
        click.echo("✅ Evolution completed successfully")
        click.echo(f"   Learning iterations: {result.get('learning_iterations', 'N/A')}")
        click.echo(f"   Strategies optimized: {result.get('strategies_optimized', 'N/A')}")
        
    except Exception as e:
        click.echo(f"❌ Evolution failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path())
@click.option("--format", "-f", type=click.Choice(["yaml", "json"]), default="yaml")
def config_create(config_file: str, format: str):
    """Create a sample configuration file."""
    click.echo(f"📝 Creating sample configuration: {config_file}")
    
    try:
        config = Config()
        config.create_sample_config(config_file)
        click.echo(f"✅ Sample configuration created: {config_file}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create config: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def config_validate(config_file: str):
    """Validate a configuration file."""
    click.echo(f"🔍 Validating configuration: {config_file}")
    
    try:
        config = Config(config_file)
        validation_result = config.validate()
        
        if validation_result["valid"]:
            click.echo("✅ Configuration is valid")
        else:
            click.echo("❌ Configuration has errors:")
            for error in validation_result["errors"]:
                click.echo(f"   - {error}")
        
        if validation_result["warnings"]:
            click.echo("⚠️  Warnings:")
            for warning in validation_result["warnings"]:
                click.echo(f"   - {warning}")
                
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--capability", "-c", help="Filter by capability")
@click.pass_context
def plugins(ctx, capability: Optional[str]):
    """List available plugins and features."""
    click.echo("🔌 Available Plugins and Features")
    
    try:
        plugins_info = asyncio.run(_get_plugins_info(ctx.obj.get("config_path"), capability))
        
        click.echo(f"📊 Total plugins: {plugins_info['total_plugins']}")
        
        if capability:
            click.echo(f"🔍 Filtered by capability: {capability}")
        
        # Show plugin statistics
        click.echo("\n📈 Capability Distribution:")
        for cap, count in sorted(plugins_info['capabilities_distribution'].items()):
            if not capability or cap == capability:
                click.echo(f"   {cap}: {count} plugins")
        
        click.echo(f"\n🎯 Feature Count: {plugins_info['feature_count']}")
        click.echo(f"📏 Max Plugins: {plugins_info['max_plugins']}")
        
    except Exception as e:
        click.echo(f"❌ Failed to get plugins info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def agents(ctx):
    """List and manage AI agents."""
    click.echo("🤖 AI Agents Status")
    
    try:
        agents_info = asyncio.run(_get_agents_info(ctx.obj.get("config_path")))
        
        for agent in agents_info:
            status_icon = "🔴" if agent["is_busy"] else "🟢"
            click.echo(f"{status_icon} {agent['name']}")
            click.echo(f"   Capabilities: {', '.join(agent['capabilities'])}")
            click.echo(f"   Performance: {agent['performance_score']:.2f}")
            click.echo(f"   Success Rate: {agent['success_rate']:.2%}")
            click.echo(f"   Tasks Completed: {agent['task_count']}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Failed to get agents info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_type")
@click.argument("data")
@click.option("--capability", "-c", multiple=True, help="Required capabilities")
@click.pass_context
def task(ctx, task_type: str, data: str, capability: tuple):
    """Execute a quick task."""
    click.echo(f"⚡ Executing quick task: {task_type}")
    
    try:
        # Parse data (try JSON first, then treat as string)
        try:
            task_data = json.loads(data)
        except json.JSONDecodeError:
            task_data = {"input": data}
        
        task = {
            "type": task_type,
            "data": task_data,
            "requirements": list(capability)
        }
        
        result = asyncio.run(_execute_task(ctx.obj.get("config_path"), task))
        
        click.echo("✅ Task completed:")
        click.echo(f"   Status: {result['status']}")
        click.echo(f"   Agent: {result.get('agent', 'N/A')}")
        click.echo(f"   Execution Time: {result.get('execution_time', 0):.2f}s")
        
        if result.get("result"):
            click.echo("📊 Result:")
            click.echo(json.dumps(result["result"], indent=2))
            
    except Exception as e:
        click.echo(f"❌ Task execution failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("OpenAGI Platform v0.1.0")
    click.echo("Comprehensive AI Platform with 30M+ Self-Learning Features")
    click.echo("Copyright (c) 2024 VIIICORP")


# Async helper functions
async def _execute_task(config_path: Optional[str], task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a task using the OpenAGI engine."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        result = await engine.process_task(task_data)
        return result
    finally:
        await engine.shutdown()


async def _execute_learning(config_path: Optional[str], training_data: Any, 
                          algorithm: str, epochs: int) -> Dict[str, Any]:
    """Execute learning with the neural network."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        
        # Create learning task
        learning_task = {
            "type": "learning_task",
            "data": {
                "training_data": training_data,
                "algorithm": algorithm,
                "epochs": epochs
            }
        }
        
        result = await engine.process_task(learning_task)
        return result
    finally:
        await engine.shutdown()


async def _get_system_status(config_path: Optional[str]) -> Dict[str, Any]:
    """Get system status."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        return engine.get_status()
    finally:
        await engine.shutdown()


async def _trigger_evolution(config_path: Optional[str]) -> Dict[str, Any]:
    """Trigger system evolution."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        await engine.evolve()
        return engine.learning_system.get_status()
    finally:
        await engine.shutdown()


async def _get_plugins_info(config_path: Optional[str], capability_filter: Optional[str]) -> Dict[str, Any]:
    """Get plugins information."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        return engine.plugin_manager.get_plugin_stats()
    finally:
        await engine.shutdown()


async def _get_agents_info(config_path: Optional[str]) -> list:
    """Get agents information."""
    config = Config(config_path) if config_path else Config()
    engine = OpenAGIEngine(config_path)
    
    try:
        await engine.initialize()
        agents_info = []
        for agent_name, agent in engine.agents.items():
            agents_info.append({
                "name": agent.name,
                "capabilities": list(agent.capabilities),
                "performance_score": agent.performance_score,
                "success_rate": agent.success_rate,
                "task_count": len(agent.task_history),
                "is_busy": agent.is_busy
            })
        return agents_info
    finally:
        await engine.shutdown()


def main():
    """Main entry point for the CLI."""
    cli()