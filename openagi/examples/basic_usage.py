#!/usr/bin/env python3
"""
OpenAGI Basic Usage Example

This example demonstrates how to use the OpenAGI platform
to perform various AI tasks.
"""

from openagi import OpenAGI


def main():
    """Main example function."""
    print("🚀 OpenAGI Basic Usage Example")
    print("=" * 40)
    
    # Initialize OpenAGI platform
    print("\n1. Initializing OpenAGI platform...")
    agi = OpenAGI()
    
    # Show platform information
    print("\n2. Platform Information:")
    info = agi.get_platform_info()
    print(f"   Version: {info['version']}")
    print(f"   Total Features: {info['total_features']}")
    print(f"   Categories: {', '.join(info['feature_categories'])}")
    
    # List available features
    print("\n3. Available Features:")
    features = agi.list_features()
    for feature_name in features:
        feature = agi.get_feature(feature_name)
        print(f"   • {feature.name} ({feature.category})")
        print(f"     {feature.description}")
    
    # Example: Text Tokenization
    print("\n4. Text Tokenization Example:")
    text = "OpenAGI is an amazing artificial intelligence platform!"
    result = agi.execute_feature("text_tokenizer", text=text, method="word")
    print(f"   Input: {result['original_text']}")
    print(f"   Tokens: {result['tokens']}")
    print(f"   Count: {result['count']}")
    
    # Example: Sentiment Analysis
    print("\n5. Sentiment Analysis Example:")
    text = "I absolutely love using this incredible AI platform!"
    result = agi.execute_feature("sentiment_analysis", text=text)
    print(f"   Input: {result['text']}")
    print(f"   Sentiment: {result['sentiment']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    
    # Example: Search Features
    print("\n6. Feature Search Example:")
    query = "text"
    results = agi.search_features(query)
    print(f"   Search query: '{query}'")
    print(f"   Found features: {', '.join(results)}")
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()