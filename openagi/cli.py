#!/usr/bin/env python3
"""
OpenAGI Command Line Interface

This module provides the CLI entry point for the OpenAGI platform.
"""

import sys
import json
import click
from pathlib import Path
from typing import Optional

from openagi import OpenAGI, __version__


@click.group()
@click.version_option(__version__)
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to configuration file')
@click.pass_context
def cli(ctx, config):
    """OpenAGI - Comprehensive AI platform with 14,000+ features."""
    ctx.ensure_object(dict)
    try:
        ctx.obj['openagi'] = OpenAGI(config_path=config)
    except Exception as e:
        click.echo(f"Error initializing OpenAGI: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """Show platform information."""
    openagi = ctx.obj['openagi']
    info_data = openagi.get_platform_info()
    
    click.echo("🚀 OpenAGI Platform Information")
    click.echo("=" * 40)
    click.echo(f"Version: {info_data['version']}")
    click.echo(f"Total Features: {info_data['total_features']}")
    click.echo(f"Categories: {', '.join(sorted(info_data['feature_categories']))}")
    click.echo("\nConfiguration:")
    for key, value in info_data['config'].items():
        click.echo(f"  {key}: {value}")


@cli.command('list-features')
@click.option('--category', '-c', help='Filter by category')
@click.pass_context
def list_features(ctx, category):
    """List all available features."""
    openagi = ctx.obj['openagi']
    features = openagi.list_features(category)
    
    title = f"Available Features" + (f" in '{category}'" if category else "")
    click.echo(f"📋 {title}")
    click.echo("=" * len(title))
    
    if not features:
        click.echo("No features found.")
        return
    
    for feature_name in sorted(features):
        feature = openagi.get_feature(feature_name)
        if feature:
            click.echo(f"• {feature.name} ({feature.category})")
            click.echo(f"  {feature.description}")
        else:
            click.echo(f"• {feature_name}")


@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search for features by name or description."""
    openagi = ctx.obj['openagi']
    results = openagi.search_features(query)
    
    click.echo(f"🔍 Search Results for '{query}'")
    click.echo("=" * 40)
    
    if not results:
        click.echo("No features found matching the query.")
        return
    
    for feature_name in sorted(results):
        feature = openagi.get_feature(feature_name)
        if feature:
            click.echo(f"• {feature.name} ({feature.category})")
            click.echo(f"  {feature.description}")


@cli.command()
@click.argument('feature_name')
@click.option('--params', '-p', help='Feature parameters as JSON string')
@click.option('--input-file', '-i', type=click.Path(exists=True),
              help='Input file path')
@click.option('--output-file', '-o', type=click.Path(),
              help='Output file path')
@click.pass_context
def run(ctx, feature_name, params, input_file, output_file):
    """Execute a specific feature."""
    openagi = ctx.obj['openagi']
    
    # Parse parameters
    kwargs = {}
    if params:
        try:
            kwargs = json.loads(params)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing parameters: {e}", err=True)
            sys.exit(1)
    
    # Handle input file
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                kwargs['text'] = f.read().strip()
        except Exception as e:
            click.echo(f"Error reading input file: {e}", err=True)
            sys.exit(1)
    
    # Execute feature
    try:
        result = openagi.execute_feature(feature_name, **kwargs)
        
        # Handle output
        output_text = json.dumps(result, indent=2)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            click.echo(f"✅ Results saved to {output_file}")
        else:
            click.echo("🎯 Feature Execution Results")
            click.echo("=" * 30)
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"Error executing feature: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode."""
    openagi = ctx.obj['openagi']
    
    click.echo("🤖 OpenAGI Interactive Mode")
    click.echo("Type 'help' for commands, 'exit' to quit")
    click.echo("=" * 40)
    
    while True:
        try:
            command = click.prompt("openagi", type=str).strip()
            
            if command.lower() in ['exit', 'quit']:
                click.echo("Goodbye!")
                break
            elif command.lower() == 'help':
                click.echo("Available commands:")
                click.echo("  list - List all features")
                click.echo("  search <query> - Search features")
                click.echo("  run <feature> - Run a feature")
                click.echo("  info - Show platform info")
                click.echo("  exit - Exit interactive mode")
            elif command.lower() == 'list':
                features = openagi.list_features()
                for feature_name in sorted(features):
                    click.echo(f"• {feature_name}")
            elif command.lower() == 'info':
                info_data = openagi.get_platform_info()
                click.echo(f"Features: {info_data['total_features']}")
                click.echo(f"Categories: {', '.join(sorted(info_data['feature_categories']))}")
            elif command.lower().startswith('search '):
                query = command[7:].strip()
                results = openagi.search_features(query)
                for feature_name in sorted(results):
                    click.echo(f"• {feature_name}")
            elif command.lower().startswith('run '):
                feature_name = command[4:].strip()
                try:
                    result = openagi.execute_feature(feature_name)
                    click.echo(json.dumps(result, indent=2))
                except Exception as e:
                    click.echo(f"Error: {e}")
            else:
                click.echo("Unknown command. Type 'help' for available commands.")
                
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break


@cli.command()
@click.pass_context
def demo(ctx):
    """Run feature demonstrations."""
    openagi = ctx.obj['openagi']
    
    click.echo("🎬 OpenAGI Feature Demonstrations")
    click.echo("=" * 40)
    
    # Demo text tokenizer
    click.echo("\n1. Text Tokenization Demo:")
    try:
        result = openagi.execute_feature("text_tokenizer", 
                                       text="Hello world! This is OpenAGI.",
                                       method="word")
        click.echo(f"   Input: {result['original_text']}")
        click.echo(f"   Tokens: {result['tokens']}")
        click.echo(f"   Count: {result['count']}")
    except Exception as e:
        click.echo(f"   Error: {e}")
    
    # Demo sentiment analysis
    click.echo("\n2. Sentiment Analysis Demo:")
    try:
        result = openagi.execute_feature("sentiment_analysis",
                                       text="I love this amazing platform!")
        click.echo(f"   Input: {result['text']}")
        click.echo(f"   Sentiment: {result['sentiment']}")
        click.echo(f"   Confidence: {result['confidence']:.2f}")
    except Exception as e:
        click.echo(f"   Error: {e}")
    
    # Demo image classification
    click.echo("\n3. Image Classification Demo:")
    try:
        result = openagi.execute_feature("image_classification",
                                       image_path="sample.jpg")
        click.echo(f"   Image: {result['image_path']}")
        click.echo(f"   Top Prediction: {result['top_prediction']}")
        click.echo(f"   Confidence: {result['confidence']:.2f}")
    except Exception as e:
        click.echo(f"   Error: {e}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()