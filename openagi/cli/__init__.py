"""
Command Line Interface for OpenAGI Platform

This module provides a comprehensive CLI for interacting with the OpenAGI platform
and its 14,000+ AI features.
"""

import click
import json
import sys
from typing import Optional, Dict, Any

from ..core import OpenAGI
from .. import __version__


@click.group()
@click.version_option(version=__version__)
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def main(ctx, config):
    """OpenAGI - Comprehensive AI Platform with 14,000+ Features"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['platform'] = OpenAGI(config_path=config)


@main.command()
@click.pass_context
def info(ctx):
    """Display platform information and statistics."""
    platform = ctx.obj['platform']
    stats = platform.get_platform_stats()
    
    click.echo("🤖 OpenAGI Platform Information")
    click.echo("=" * 40)
    click.echo(f"Version: {__version__}")
    click.echo(f"Total Features: {stats['total_features']:,}")
    click.echo(f"Categories: {stats['categories']}")
    click.echo("\nFeature Breakdown by Category:")
    
    for category, count in stats['category_breakdown'].items():
        click.echo(f"  • {category.replace('_', ' ').title()}: {count:,} features")


@main.command()
@click.argument('query')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'list']),
              help='Output format')
@click.pass_context
def search(ctx, query, format):
    """Search for AI features by name or description."""
    platform = ctx.obj['platform']
    results = platform.search_features(query)
    
    if not results:
        click.echo(f"No features found matching '{query}'")
        return
    
    if format == 'json':
        click.echo(json.dumps(results, indent=2))
    elif format == 'list':
        for result in results:
            click.echo(f"• {result['name']} ({result['category']})")
    else:  # table format
        click.echo(f"\nFound {len(results)} features matching '{query}':")
        click.echo("-" * 60)
        for result in results:
            click.echo(f"Name: {result['name']}")
            click.echo(f"Category: {result['category']}")
            click.echo(f"Description: {result['description']}")
            click.echo("-" * 60)


@main.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'list']),
              help='Output format')
@click.pass_context
def list_features(ctx, category, format):
    """List all available AI features."""
    platform = ctx.obj['platform']
    
    if category:
        features = platform.registry.get_features_by_category(category)
        feature_list = [{"name": f.name, "category": f.category, "description": f.description} 
                       for f in features]
    else:
        feature_list = []
        all_features = platform.list_available_features()
        for cat, feat_names in all_features.items():
            for name in feat_names:
                info = platform.get_feature_info(name)
                if info:
                    feature_list.append({
                        "name": info.name,
                        "category": info.category,
                        "description": info.description
                    })
    
    if format == 'json':
        click.echo(json.dumps(feature_list, indent=2))
    elif format == 'list':
        for feature in feature_list:
            click.echo(f"• {feature['name']}")
    else:  # table format
        click.echo(f"\nAvailable Features ({len(feature_list)} total):")
        click.echo("=" * 80)
        for feature in feature_list[:50]:  # Limit display for readability
            click.echo(f"{feature['name']:<30} | {feature['category']:<20} | {feature['description']}")
        
        if len(feature_list) > 50:
            click.echo(f"\n... and {len(feature_list) - 50} more features.")
            click.echo("Use --format json to see all features.")


@main.command()
@click.pass_context
def categories(ctx):
    """List all feature categories."""
    platform = ctx.obj['platform']
    categories = platform.registry.list_categories()
    
    click.echo("🗂️  Feature Categories:")
    click.echo("=" * 30)
    
    for category in sorted(categories):
        count = len(platform.registry.get_features_by_category(category))
        click.echo(f"• {category.replace('_', ' ').title():<25} ({count:,} features)")


@main.command()
@click.argument('feature_name')
@click.pass_context
def describe(ctx, feature_name):
    """Get detailed information about a specific feature."""
    platform = ctx.obj['platform']
    feature_info = platform.get_feature_info(feature_name)
    
    if not feature_info:
        click.echo(f"❌ Feature '{feature_name}' not found.")
        click.echo("Use 'openagi search <query>' to find features.")
        return
    
    click.echo(f"🔧 Feature: {feature_info.name}")
    click.echo("=" * 50)
    click.echo(f"Category: {feature_info.category}")
    click.echo(f"Description: {feature_info.description}")
    click.echo(f"Version: {feature_info.version}")
    click.echo(f"Author: {feature_info.author}")
    
    if feature_info.tags:
        click.echo(f"Tags: {', '.join(feature_info.tags)}")
    
    if feature_info.dependencies:
        click.echo(f"Dependencies: {', '.join(feature_info.dependencies)}")


@main.command()
@click.argument('feature_name')
@click.option('--params', '-p', help='JSON parameters for the feature')
@click.option('--input-file', '-i', help='Input file path')
@click.option('--output-file', '-o', help='Output file path')
@click.pass_context
def run(ctx, feature_name, params, input_file, output_file):
    """Execute a specific AI feature."""
    platform = ctx.obj['platform']
    
    # Parse parameters
    feature_params = {}
    if params:
        try:
            feature_params = json.loads(params)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON parameters")
            return
    
    # Handle input file
    input_data = None
    if input_file:
        try:
            with open(input_file, 'r') as f:
                if input_file.endswith('.json'):
                    input_data = json.load(f)
                else:
                    input_data = f.read()
        except Exception as e:
            click.echo(f"❌ Error reading input file: {e}")
            return
    
    # Execute feature
    try:
        if input_data:
            result = platform.execute_feature(feature_name, input_data, **feature_params)
        else:
            result = platform.execute_feature(feature_name, **feature_params)
        
        # Handle output
        if output_file:
            with open(output_file, 'w') as f:
                if isinstance(result, dict):
                    json.dump(result, f, indent=2)
                else:
                    f.write(str(result))
            click.echo(f"✅ Result saved to {output_file}")
        else:
            if isinstance(result, dict):
                click.echo("🎯 Execution Result:")
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(f"🎯 Result: {result}")
                
    except Exception as e:
        click.echo(f"❌ Error executing feature: {e}")


@main.command()
@click.pass_context
def demo(ctx):
    """Run a demonstration of various OpenAGI features."""
    platform = ctx.obj['platform']
    
    click.echo("🚀 OpenAGI Platform Demo")
    click.echo("=" * 40)
    
    demos = [
        {
            "feature": "text_tokenizer",
            "input": "Hello world, this is OpenAGI!",
            "params": {"method": "word"}
        },
        {
            "feature": "sentiment_analyzer", 
            "input": "I love using OpenAGI, it's amazing!",
            "params": {}
        },
        {
            "feature": "keyword_extractor",
            "input": "OpenAGI is a comprehensive artificial intelligence platform with thousands of features",
            "params": {"max_keywords": 5}
        }
    ]
    
    for demo in demos:
        feature_name = demo["feature"]
        click.echo(f"\n🔧 Demonstrating: {feature_name}")
        click.echo("-" * 30)
        
        try:
            result = platform.execute_feature(feature_name, demo["input"], **demo["params"])
            click.echo(f"Input: {demo['input']}")
            click.echo(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            click.echo(f"❌ Demo failed: {e}")
    
    click.echo(f"\n✨ Demo complete! Explore {platform.get_platform_stats()['total_features']:,} more features.")


if __name__ == '__main__':
    main()