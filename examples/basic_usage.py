#!/usr/bin/env python3
"""
OpenAGI Examples - Comprehensive AI Platform Usage Examples

This script demonstrates various features of the OpenAGI platform.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from openagi import OpenAGI

def main():
    print("🤖 OpenAGI Platform Examples")
    print("=" * 50)
    
    # Initialize the platform
    platform = OpenAGI()
    
    # Display platform statistics
    stats = platform.get_platform_stats()
    print(f"Total features available: {stats['total_features']:,}")
    print(f"Categories: {stats['categories']}")
    print()
    
    # Example 1: Natural Language Processing
    print("📝 NLP Examples:")
    print("-" * 20)
    
    text = "OpenAGI is an amazing artificial intelligence platform with thousands of features!"
    
    # Sentiment analysis
    sentiment = platform.execute_feature("sentiment_analyzer", text)
    print(f"Sentiment: {sentiment}")
    
    # Keyword extraction
    keywords = platform.execute_feature("keyword_extractor", text, max_keywords=5)
    print(f"Keywords: {keywords}")
    
    # Language detection
    language = platform.execute_feature("language_detector", text)
    print(f"Language: {language}")
    print()
    
    # Example 2: Computer Vision
    print("👁️ Computer Vision Examples:")
    print("-" * 30)
    
    # Create a sample image (random data)
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Object detection
    objects = platform.execute_feature("object_detector", image)
    print(f"Objects detected: {len(objects)}")
    
    # Face detection
    faces = platform.execute_feature("face_detector", image)
    print(f"Faces detected: {len(faces)}")
    
    # Image enhancement
    enhanced_image = platform.execute_feature("image_enhancer", image, enhancement_type="contrast")
    print(f"Image enhanced: {enhanced_image.shape}")
    print()
    
    # Example 3: Machine Learning
    print("🤖 Machine Learning Examples:")
    print("-" * 30)
    
    # Generate sample data
    X = np.random.randn(100, 4)
    y = np.random.randint(0, 2, 100)
    
    # Train a classifier
    ml_result = platform.execute_feature("random_forest_classifier", X, y, n_trees=10)
    print(f"Random Forest trained: {ml_result['status']}")
    
    # Clustering
    cluster_result = platform.execute_feature("kmeans_clusterer", X, k=3)
    print(f"K-means clustering completed with {len(set(cluster_result['labels']))} clusters")
    
    # Dimensionality reduction
    pca_result = platform.execute_feature("pca_reducer", X, n_components=2)
    print(f"PCA reduction: {X.shape} -> {np.array(pca_result['transformed_data']).shape}")
    print()
    
    # Example 4: Audio Processing
    print("🎵 Audio Processing Examples:")
    print("-" * 30)
    
    # Generate sample audio data
    sample_rate = 44100
    duration = 2  # seconds
    audio = np.random.randn(sample_rate * duration)
    
    # Audio feature extraction
    audio_features = platform.execute_feature("audio_feature_extractor", audio, sample_rate=sample_rate)
    print(f"Audio duration: {audio_features['duration']:.2f} seconds")
    print(f"RMS energy: {audio_features['rms_energy']:.4f}")
    
    # Audio enhancement
    enhanced_audio = platform.execute_feature("audio_enhancer", audio, enhancement_type="normalize")
    print(f"Audio enhanced: {enhanced_audio.shape}")
    print()
    
    # Example 5: Data Analysis
    print("📊 Data Analysis Examples:")
    print("-" * 25)
    
    # Generate sample data
    data = np.random.normal(10, 2, 1000)
    
    # Statistical analysis
    data_stats = {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data))
    }
    print(f"Data statistics:")
    print(f"  Mean: {data_stats['mean']:.2f}")
    print(f"  Std: {data_stats['std']:.2f}")
    print(f"  Min: {data_stats['min']:.2f}")
    print(f"  Max: {data_stats['max']:.2f}")
    print()
    
    # Example 6: Feature Search and Discovery
    print("🔍 Feature Discovery:")
    print("-" * 20)
    
    # Search for features
    search_results = platform.search_features("text")
    print(f"Found {len(search_results)} features related to 'text'")
    
    # List features by category
    cv_features = platform.registry.get_features_by_category("computer_vision")
    print(f"Computer Vision features: {len(cv_features)}")
    
    nlp_features = platform.registry.get_features_by_category("nlp")
    print(f"NLP features: {len(nlp_features)}")
    print()
    
    # Example 7: Automation
    print("⚡ Automation Examples:")
    print("-" * 22)
    
    # Task scheduling
    tasks = [
        {"name": "Data Processing", "priority": "high"},
        {"name": "Report Generation", "priority": "medium"},
        {"name": "Backup", "priority": "low"}
    ]
    
    # Task scheduling simulation
    schedule_result = {
        "total_tasks": len(tasks),
        "status": "scheduled"
    }
    print(f"Scheduled {schedule_result['total_tasks']} tasks")
    print()
    
    print("✨ Examples completed successfully!")
    print(f"Explore {platform.get_platform_stats()['total_features']:,} more features in OpenAGI!")

if __name__ == "__main__":
    main()