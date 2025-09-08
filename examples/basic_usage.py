#!/usr/bin/env python3
"""
Basic OpenAGI Usage Example

This example demonstrates the basic usage of the OpenAGI platform
including initializing the platform, listing features, and executing them.
"""

from openagi import OpenAGI


def main():
    """Run basic OpenAGI examples."""
    print("🤖 OpenAGI Basic Usage Example")
    print("=" * 40)
    
    # Initialize the platform
    print("Initializing OpenAGI platform...")
    platform = OpenAGI()
    
    # Get platform statistics
    stats = platform.get_platform_stats()
    print(f"✅ Platform loaded with {stats['total_features']:,} features")
    print(f"📁 Available categories: {stats['categories']}")
    
    # List available features by category
    print("\n📋 Feature Categories:")
    features_by_category = platform.list_available_features()
    for category, feature_names in features_by_category.items():
        print(f"  • {category.replace('_', ' ').title()}: {len(feature_names)} features")
    
    # Search for features
    print("\n🔍 Searching for 'text' features:")
    text_features = platform.search_features("text")
    for feature in text_features[:3]:  # Show first 3
        print(f"  • {feature['name']}: {feature['description']}")
    
    # Execute some example features
    print("\n🚀 Executing Example Features:")
    
    try:
        # Text tokenization example
        result = platform.execute_feature(
            "text_tokenizer",
            "OpenAGI is an amazing AI platform!",
            method="word"
        )
        print(f"✅ Tokenization result: {result['count']} tokens")
        print(f"   Tokens: {result['tokens'][:5]}...")  # Show first 5 tokens
        
        # Sentiment analysis example
        result = platform.execute_feature(
            "sentiment_analyzer",
            "I love using OpenAGI, it's fantastic!"
        )
        print(f"✅ Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2f})")
        
        # Keyword extraction example
        result = platform.execute_feature(
            "keyword_extractor",
            "OpenAGI provides comprehensive artificial intelligence capabilities",
            max_keywords=3
        )
        print(f"✅ Keywords extracted: {len(result['keywords'])}")
        for kw in result['keywords']:
            print(f"   - {kw['word']} (frequency: {kw['frequency']})")
            
    except Exception as e:
        print(f"❌ Error executing feature: {e}")
    
    print("\n🎉 Example complete! Try the CLI with: openagi --help")


if __name__ == "__main__":
    main()