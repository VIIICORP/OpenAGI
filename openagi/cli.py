"""Command-line interface for OpenAGI."""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any

from openagi.core.platform import OpenAGI
from openagi.core.config import Config
from openagi.api.client import OpenAGIClient


@click.group()
@click.version_option()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """OpenAGI - Open-source AGI platform with 20,000+ AI models."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--workers', default=4, help='Number of worker processes')
@click.option('--dev', is_flag=True, help='Development mode')
@click.pass_context
def serve(ctx, host, port, workers, dev):
    """Start the OpenAGI server."""
    config_path = ctx.obj.get('config_path')
    
    try:
        # Initialize platform
        agi = OpenAGI(config_path)
        
        click.echo(f"🚀 Starting OpenAGI server on {host}:{port}")
        click.echo(f"📊 Platform stats: {agi.get_stats()}")
        
        if dev:
            click.echo("🔧 Running in development mode")
            # Development server (simplified)
            _run_dev_server(agi, host, port)
        else:
            click.echo(f"⚡ Production server with {workers} workers")
            _run_production_server(agi, host, port, workers)
            
    except Exception as e:
        click.echo(f"❌ Failed to start server: {e}", err=True)
        sys.exit(1)


def _run_dev_server(agi, host, port):
    """Run development server."""
    try:
        import uvicorn
        from ..api.server import create_app
        
        app = create_app(agi)
        uvicorn.run(app, host=host, port=port, reload=True)
        
    except ImportError:
        click.echo("❌ uvicorn not installed. Install with: pip install uvicorn", err=True)
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
    finally:
        agi.shutdown()


def _run_production_server(agi, host, port, workers):
    """Run production server."""
    try:
        import uvicorn
        from ..api.server import create_app
        
        app = create_app(agi)
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            access_log=True
        )
        
    except ImportError:
        click.echo("❌ uvicorn not installed. Install with: pip install uvicorn", err=True)
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
    finally:
        agi.shutdown()


@cli.group()
def models():
    """Model management commands."""
    pass


@models.command('list')
@click.option('--category', '-c', help='Filter by category')
@click.option('--provider', '-p', help='Filter by provider')
@click.option('--size', '-s', help='Filter by size')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'csv']), help='Output format')
@click.pass_context
def list_models(ctx, category, provider, size, output_format):
    """List available models."""
    config_path = ctx.obj.get('config_path')
    
    try:
        agi = OpenAGI(config_path)
        models_list = agi.models.list(category=category, provider=provider, size=size)
        
        if output_format == 'json':
            data = [
                {
                    'id': m.id,
                    'name': m.name,
                    'category': m.category.value,
                    'provider': m.provider,
                    'size': m.size,
                    'parameters': m.parameters
                }
                for m in models_list[:50]  # Limit output
            ]
            click.echo(json.dumps(data, indent=2))
            
        elif output_format == 'csv':
            click.echo('id,name,category,provider,size,parameters')
            for m in models_list[:50]:
                click.echo(f'{m.id},{m.name},{m.category.value},{m.provider},{m.size},{m.parameters}')
                
        else:  # table
            click.echo(f"\n📋 Found {len(models_list)} models")
            click.echo(f"{'ID':<20} {'Name':<30} {'Category':<12} {'Size':<8} {'Provider':<15}")
            click.echo("-" * 90)
            
            for model in models_list[:50]:  # Limit output
                click.echo(f"{model.id:<20} {model.name[:29]:<30} {model.category.value:<12} "
                          f"{model.size:<8} {model.provider:<15}")
                          
        if len(models_list) > 50:
            click.echo(f"\n... and {len(models_list) - 50} more models")
            
    except Exception as e:
        click.echo(f"❌ Error listing models: {e}", err=True)
        sys.exit(1)


@models.command('search')
@click.argument('query')
@click.option('--category', '-c', help='Filter by category')
@click.option('--limit', '-l', default=10, help='Limit results')
@click.pass_context
def search_models(ctx, query, category, limit):
    """Search for models."""
    config_path = ctx.obj.get('config_path')
    
    try:
        agi = OpenAGI(config_path)
        results = agi.search_models(query, category)
        
        click.echo(f"\n🔍 Search results for '{query}' ({len(results)} found)")
        click.echo(f"{'ID':<20} {'Name':<30} {'Category':<12} {'Description'}")
        click.echo("-" * 100)
        
        for model in results[:limit]:
            desc = model.description[:40] + "..." if len(model.description) > 40 else model.description
            click.echo(f"{model.id:<20} {model.name[:29]:<30} {model.category.value:<12} {desc}")
            
    except Exception as e:
        click.echo(f"❌ Error searching models: {e}", err=True)
        sys.exit(1)


@models.command('info')
@click.argument('model_id')
@click.pass_context
def model_info(ctx, model_id):
    """Get detailed information about a model."""
    config_path = ctx.obj.get('config_path')
    
    try:
        agi = OpenAGI(config_path)
        model = agi.models.get(model_id)
        
        if not model:
            click.echo(f"❌ Model '{model_id}' not found", err=True)
            sys.exit(1)
            
        click.echo(f"\n📋 Model Information: {model.name}")
        click.echo(f"ID: {model.id}")
        click.echo(f"Category: {model.category.value}")
        click.echo(f"Provider: {model.provider}")
        click.echo(f"Type: {model.model_type}")
        click.echo(f"Size: {model.size}")
        click.echo(f"Parameters: {model.parameters:,}")
        click.echo(f"License: {model.license}")
        click.echo(f"Description: {model.description}")
        click.echo(f"Capabilities: {', '.join(model.capabilities)}")
        click.echo(f"Languages: {', '.join(model.languages)}")
        click.echo(f"Modalities: {', '.join(model.modalities)}")
        
        if model.huggingface_id:
            click.echo(f"Hugging Face: {model.huggingface_id}")
            
    except Exception as e:
        click.echo(f"❌ Error getting model info: {e}", err=True)
        sys.exit(1)


@cli.group()
def agents():
    """Agent management commands."""
    pass


@agents.command('create')
@click.argument('agent_type', type=click.Choice(['conversational', 'vision', 'multimodal']))
@click.option('--name', '-n', help='Agent name')
@click.option('--config-file', help='Agent configuration file')
@click.pass_context
def create_agent(ctx, agent_type, name, config_file):
    """Create a new agent."""
    config_path = ctx.obj.get('config_path')
    
    try:
        agi = OpenAGI(config_path)
        
        agent_config = {}
        if config_file:
            with open(config_file) as f:
                agent_config = json.load(f)
                
        agent = agi.agents.create_agent(agent_type, name, agent_config)
        
        click.echo(f"✅ Created {agent_type} agent: {agent.name} ({agent.id})")
        click.echo(f"Capabilities: {[cap.name for cap in agent.capabilities]}")
        
    except Exception as e:
        click.echo(f"❌ Error creating agent: {e}", err=True)
        sys.exit(1)


@agents.command('list')
@click.option('--status', help='Filter by status')
@click.pass_context
def list_agents(ctx, status):
    """List agents."""
    config_path = ctx.obj.get('config_path')
    
    try:
        agi = OpenAGI(config_path)
        
        from ..agents.base import AgentStatus
        status_filter = None
        if status:
            try:
                status_filter = AgentStatus(status)
            except ValueError:
                click.echo(f"❌ Invalid status: {status}", err=True)
                sys.exit(1)
                
        agents_list = agi.agents.list_agents(status_filter)
        
        click.echo(f"\n🤖 Found {len(agents_list)} agents")
        click.echo(f"{'ID':<20} {'Name':<25} {'Type':<15} {'Status':<10} {'Tasks'}")
        click.echo("-" * 80)
        
        for agent in agents_list:
            agent_type = agent.__class__.__name__
            task_count = len(agent.task_history)
            click.echo(f"{agent.id[:19]:<20} {agent.name[:24]:<25} {agent_type:<15} "
                      f"{agent.status.value:<10} {task_count}")
                      
    except Exception as e:
        click.echo(f"❌ Error listing agents: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--url', default='http://localhost:8000', help='API URL')
@click.option('--api-key', help='API key')
@click.pass_context
def status(ctx, url, api_key):
    """Get platform status."""
    try:
        client = OpenAGIClient(url, api_key)
        status_data = client.get_status()
        
        click.echo("🚀 OpenAGI Platform Status")
        click.echo(f"Total Models: {status_data.get('total_models', 0):,}")
        click.echo(f"Categories: {len(status_data.get('categories', {}))}")
        click.echo(f"Active Agents: {status_data.get('active_agents', 0)}")
        
        health = client.get_health()
        click.echo(f"Health: {'✅ Healthy' if health.get('status') == 'healthy' else '❌ Unhealthy'}")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('prompt')
@click.option('--model', default='llama2-7b-chat', help='Model to use')
@click.option('--url', default='http://localhost:8000', help='API URL')
@click.option('--api-key', help='API key')
def chat(prompt, model, url, api_key):
    """Quick chat with AI model."""
    try:
        client = OpenAGIClient(url, api_key)
        response = client.quick_chat(prompt, model)
        
        click.echo(f"\n🤖 {model}:")
        click.echo(response)
        
    except Exception as e:
        click.echo(f"❌ Chat failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--model', default='resnet-50', help='Model to use')
@click.option('--url', default='http://localhost:8000', help='API URL')
@click.option('--api-key', help='API key')
def analyze(image_path, model, url, api_key):
    """Analyze an image."""
    try:
        client = OpenAGIClient(url, api_key)
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            
        result = client.analyze_image(image_data, model)
        
        click.echo(f"\n📸 Analysis of {image_path}:")
        click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config-path', help='Configuration file path')
@click.option('--output', '-o', help='Output file path')
def init(config_path, output):
    """Initialize OpenAGI configuration."""
    config = Config()
    
    output_path = output or config_path or "openagi.yaml"
    
    try:
        config.save(output_path)
        click.echo(f"✅ Configuration initialized: {output_path}")
        click.echo("Edit the configuration file and run 'openagi serve' to start the platform")
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize config: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()