# User Guide

Complete guide to using OpenAGI's 14,000+ AI features across all categories.

## 📚 Table of Contents

- [Getting Started](#getting-started)
- [Feature Categories](#feature-categories)
- [Using the Python API](#using-the-python-api)
- [Using the CLI](#using-the-cli)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

## 🚀 Getting Started

### Basic Usage Pattern

```python
from openagi import OpenAGI

# Initialize the platform
agi = OpenAGI()

# Execute a feature
result = agi.run('feature_name', **parameters)

# Process results
print(result)
```

### Feature Discovery

```python
# List all categories
categories = agi.list_categories()

# List features in a category
nlp_features = agi.list_features(category='nlp')

# Search for features
sentiment_features = agi.search_features('sentiment')

# Get feature information
info = agi.get_feature_info('text_sentiment_analysis')
```

## 🔍 Feature Categories

### 🧠 Natural Language Processing (2,000+ features)

#### Text Analysis
```python
# Sentiment analysis
result = agi.run('text_sentiment_analysis', 
                text="I love this product!")
# Returns: {'sentiment': 'positive', 'confidence': 0.92}

# Language detection
result = agi.run('text_language_detection',
                text="Bonjour le monde")
# Returns: {'language': 'fr', 'confidence': 0.98}

# Entity extraction
result = agi.run('text_entity_extraction',
                text="John works at Apple in California")
# Returns: {'entities': [{'text': 'John', 'type': 'PERSON'}, ...]}
```

#### Text Processing
```python
# Text cleaning
result = agi.run('text_cleaner',
                text="  Hello!!! World???  ",
                remove_punctuation=True,
                normalize_whitespace=True)

# Text summarization
result = agi.run('text_summarization',
                text=long_article,
                max_length=100)

# Keyword extraction
result = agi.run('text_keyword_extraction',
                text=document,
                num_keywords=10)
```

#### Text Generation
```python
# Text completion
result = agi.run('text_completion',
                prompt="The future of AI is",
                max_length=50)

# Text translation
result = agi.run('text_translation',
                text="Hello world",
                source_lang="en",
                target_lang="es")
```

### 👁️ Computer Vision (2,500+ features)

#### Image Processing
```python
# Image resize
result = agi.run('image_resize',
                image_path="photo.jpg",
                width=800,
                height=600)

# Image enhancement
result = agi.run('image_enhance',
                image_path="dark_photo.jpg",
                brightness=1.2,
                contrast=1.1)

# Image filtering
result = agi.run('image_blur',
                image_path="image.jpg",
                blur_radius=5)
```

#### Object Detection
```python
# Detect objects
result = agi.run('image_object_detection',
                image_path="scene.jpg")
# Returns: {'objects': [{'class': 'car', 'confidence': 0.95, 'bbox': [...]}, ...]}

# Face detection
result = agi.run('image_face_detection',
                image_path="group_photo.jpg")

# Landmark detection
result = agi.run('image_landmark_detection',
                image_path="building.jpg")
```

#### Feature Extraction
```python
# SIFT features
result = agi.run('image_sift_features',
                image_path="texture.jpg")

# Color histogram
result = agi.run('image_color_histogram',
                image_path="colorful.jpg",
                bins=32)

# Edge detection
result = agi.run('image_edge_detection',
                image_path="photo.jpg",
                method="canny")
```

### 🤖 Machine Learning (2,000+ features)

#### Classification
```python
# Train classifier
result = agi.run('ml_train_classifier',
                data=training_data,
                target=labels,
                algorithm="random_forest")

# Make predictions
result = agi.run('ml_predict',
                model=trained_model,
                data=test_data)

# Evaluate model
result = agi.run('ml_evaluate_classifier',
                model=model,
                test_data=test_data,
                test_labels=test_labels)
```

#### Clustering
```python
# K-means clustering
result = agi.run('ml_kmeans_clustering',
                data=dataset,
                n_clusters=5)

# DBSCAN clustering
result = agi.run('ml_dbscan_clustering',
                data=dataset,
                eps=0.5,
                min_samples=5)
```

#### Dimensionality Reduction
```python
# PCA
result = agi.run('ml_pca',
                data=high_dim_data,
                n_components=2)

# t-SNE
result = agi.run('ml_tsne',
                data=dataset,
                n_components=2,
                perplexity=30)
```

### 🎵 Audio Processing (1,000+ features)

#### Audio Analysis
```python
# Audio transcription
result = agi.run('audio_transcription',
                audio_path="speech.wav")

# Music genre classification
result = agi.run('audio_genre_classification',
                audio_path="song.mp3")

# Audio feature extraction
result = agi.run('audio_mfcc_extraction',
                audio_path="audio.wav",
                n_mfcc=13)
```

#### Audio Enhancement
```python
# Noise reduction
result = agi.run('audio_noise_reduction',
                audio_path="noisy_audio.wav")

# Audio normalization
result = agi.run('audio_normalize',
                audio_path="quiet_audio.wav")

# Echo removal
result = agi.run('audio_echo_removal',
                audio_path="echo_audio.wav")
```

### 📊 Data Analysis (1,500+ features)

#### Statistical Analysis
```python
# Descriptive statistics
result = agi.run('data_descriptive_stats',
                data=dataset)

# Correlation analysis
result = agi.run('data_correlation_analysis',
                data=dataframe,
                method="pearson")

# Hypothesis testing
result = agi.run('data_t_test',
                group1=sample1,
                group2=sample2)
```

#### Data Visualization
```python
# Create scatter plot
result = agi.run('data_scatter_plot',
                x=x_data,
                y=y_data,
                title="My Scatter Plot")

# Generate histogram
result = agi.run('data_histogram',
                data=values,
                bins=20)

# Create heatmap
result = agi.run('data_heatmap',
                data=correlation_matrix)
```

### ⚡ Automation (1,000+ features)

#### Workflow Automation
```python
# Schedule task
result = agi.run('automation_schedule_task',
                task=task_function,
                schedule="daily",
                time="09:00")

# Email automation
result = agi.run('automation_send_email',
                to="user@example.com",
                subject="Automated Report",
                body=report_content)

# File monitoring
result = agi.run('automation_monitor_directory',
                path="/data/incoming",
                callback=process_new_file)
```

## 🖥️ Using the CLI

### Basic Commands

```bash
# Show platform information
openagi info

# List features
openagi list-features
openagi list-features --category nlp
openagi list-features --category computer_vision --limit 10

# Search features
openagi search "sentiment"
openagi search "object detection"

# Get feature help
openagi help text_sentiment_analysis
openagi params image_resize
```

### Execute Features

```bash
# Execute with parameters
openagi run text_sentiment_analysis --text "I love this!"

# Execute with input file
openagi run image_resize --image-path photo.jpg --width 800 --height 600

# Execute with JSON parameters
openagi run ml_train_classifier --params '{"algorithm": "random_forest", "n_estimators": 100}'

# Pipeline execution
openagi run text_cleaner --text "messy text" | openagi run text_sentiment_analysis
```

### Interactive Mode

```bash
# Start interactive mode
openagi interactive

# In interactive mode:
> list-features --category nlp
> run text_sentiment_analysis --text "Hello world"
> help image_object_detection
> exit
```

### Batch Processing

```bash
# Process multiple files
openagi batch-run image_resize --input-dir ./images --width 800 --height 600

# Run from configuration file
openagi run-config batch_config.yaml
```

## ⚙️ Configuration

### Configuration File (config.yaml)

```yaml
# OpenAGI Configuration
logging_level: INFO
auto_load_features: true
feature_timeout: 300
enable_caching: true
max_concurrent_features: 10

# Feature-specific settings
nlp:
  default_language: "en"
  max_text_length: 10000
  models:
    sentiment: "distilbert-base-uncased"
    translation: "helsinki-nlp/opus-mt-en-es"

computer_vision:
  default_image_format: "RGB"
  max_image_size: [1920, 1080]
  models:
    object_detection: "yolov8n"
    face_detection: "mtcnn"

machine_learning:
  default_random_state: 42
  cross_validation_folds: 5
  auto_tune_hyperparameters: false

audio_processing:
  default_sample_rate: 44100
  max_audio_length: 300

# API settings
api:
  rate_limit: 1000
  timeout: 30
  enable_cors: true

# Cache settings
cache:
  enabled: true
  max_size: "1GB"
  ttl: 3600
  backend: "redis"  # or "memory", "disk"

# GPU settings
gpu:
  enabled: true
  memory_fraction: 0.8
  allow_growth: true
```

### Environment Variables

```bash
# Configuration
export OPENAGI_CONFIG_PATH="/path/to/config.yaml"
export OPENAGI_LOG_LEVEL="DEBUG"
export OPENAGI_CACHE_DIR="/tmp/openagi_cache"

# API Keys (for external services)
export OPENAI_API_KEY="your_openai_key"
export HUGGINGFACE_API_KEY="your_hf_key"

# GPU settings
export CUDA_VISIBLE_DEVICES="0,1"
```

### Runtime Configuration

```python
from openagi import OpenAGI

# Configure at runtime
agi = OpenAGI(
    config_path="custom_config.yaml",
    cache_enabled=True,
    log_level="INFO"
)

# Update configuration
agi.update_config({
    'nlp': {
        'max_text_length': 5000
    }
})
```

## 🎯 Best Practices

### Error Handling

```python
from openagi import OpenAGI, OpenAGIError

agi = OpenAGI()

try:
    result = agi.run('text_sentiment_analysis', text="")
except OpenAGIError as e:
    print(f"OpenAGI error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Performance Optimization

```python
# Use caching for repeated operations
agi = OpenAGI(cache_enabled=True)

# Batch processing for multiple items
texts = ["text1", "text2", "text3"]
results = agi.batch_run('text_sentiment_analysis', 
                       [{'text': t} for t in texts])

# Async execution for I/O bound operations
import asyncio

async def process_async():
    result = await agi.arun('text_sentiment_analysis', 
                           text="async processing")
    return result
```

### Resource Management

```python
# Limit concurrent features
agi = OpenAGI(max_concurrent_features=5)

# Set timeouts
result = agi.run('long_running_feature', 
                timeout=600)  # 10 minutes

# Memory management
agi.clear_cache()  # Clear cached results
agi.gc_collect()   # Force garbage collection
```

### Model Management

```python
# Preload models for better performance
agi.preload_models(['text_sentiment_analysis', 'image_object_detection'])

# Update models
agi.update_model('text_sentiment_analysis', 'new_model_path')

# List loaded models
loaded_models = agi.list_loaded_models()
```

## 🔧 Advanced Usage

### Custom Feature Pipelines

```python
# Create a custom pipeline
pipeline = agi.create_pipeline([
    ('text_cleaner', {'remove_punctuation': True}),
    ('text_sentiment_analysis', {}),
    ('data_confidence_filter', {'min_confidence': 0.8})
])

# Execute pipeline
result = pipeline.run(text="Messy input text!!!")
```

### Feature Composition

```python
# Compose features
def analyze_document(text):
    # Clean text
    clean_text = agi.run('text_cleaner', text=text)
    
    # Extract entities
    entities = agi.run('text_entity_extraction', text=clean_text)
    
    # Analyze sentiment
    sentiment = agi.run('text_sentiment_analysis', text=clean_text)
    
    # Summarize
    summary = agi.run('text_summarization', text=clean_text)
    
    return {
        'entities': entities,
        'sentiment': sentiment,
        'summary': summary
    }
```

### Custom Configuration Profiles

```python
# Development profile
dev_config = {
    'logging_level': 'DEBUG',
    'cache_enabled': False,
    'feature_timeout': 60
}

# Production profile  
prod_config = {
    'logging_level': 'INFO',
    'cache_enabled': True,
    'feature_timeout': 300,
    'max_concurrent_features': 20
}

# Load profile
agi = OpenAGI(config=prod_config)
```

## 📊 Monitoring and Debugging

### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('openagi')

# Feature execution logging
result = agi.run('text_sentiment_analysis', 
                text="test", 
                verbose=True)
```

### Metrics

```python
# Get execution metrics
metrics = agi.get_metrics()
print(f"Features executed: {metrics['total_executions']}")
print(f"Average execution time: {metrics['avg_execution_time']}")

# Feature-specific metrics
feature_metrics = agi.get_feature_metrics('text_sentiment_analysis')
```

### Debugging

```python
# Debug mode
agi = OpenAGI(debug=True)

# Dry run (validate without execution)
result = agi.dry_run('text_sentiment_analysis', text="test")

# Explain feature execution
explanation = agi.explain_feature('text_sentiment_analysis')
```

## 📞 Getting Help

- **Feature not working?** Check [Troubleshooting Guide](Troubleshooting.md)
- **Need examples?** Browse [Examples](Examples.md)
- **API questions?** See [API Reference](API-Reference.md)
- **Performance issues?** Check [Performance Guide](Performance.md)

---

Ready to explore specific features? Check out the [Feature Categories](Feature-Categories.md) for detailed documentation on each category.