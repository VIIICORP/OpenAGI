# API Reference

Complete reference for OpenAGI's Python API and REST endpoints.

## 📚 Table of Contents

- [Python API](#python-api)
- [REST API](#rest-api)
- [CLI Interface](#cli-interface)
- [Configuration API](#configuration-api)
- [Error Handling](#error-handling)

## 🐍 Python API

### Core Classes

#### OpenAGI

Main platform class for accessing all AI features.

```python
class OpenAGI:
    """Main OpenAGI platform class."""
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 config: Optional[Dict] = None,
                 cache_enabled: bool = True,
                 log_level: str = "INFO",
                 max_concurrent_features: int = 10):
        """Initialize OpenAGI platform.
        
        Args:
            config_path: Path to configuration file
            config: Configuration dictionary
            cache_enabled: Enable result caching
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            max_concurrent_features: Maximum concurrent feature executions
        """
```

#### Key Methods

##### run()
Execute a single feature with parameters.

```python
def run(self, 
        feature_name: str, 
        timeout: Optional[int] = None,
        **kwargs) -> Dict[str, Any]:
    """Execute a feature.
    
    Args:
        feature_name: Name of the feature to execute
        timeout: Execution timeout in seconds
        **kwargs: Feature-specific parameters
        
    Returns:
        Dictionary containing feature results
        
    Raises:
        FeatureNotFoundError: If feature doesn't exist
        FeatureExecutionError: If execution fails
        TimeoutError: If execution times out
    """

# Examples
result = agi.run('text_sentiment_analysis', text="I love this!")
result = agi.run('image_resize', image_path="photo.jpg", width=800, height=600)
result = agi.run('ml_train_classifier', data=X, target=y, algorithm="svm")
```

##### batch_run()
Execute a feature multiple times with different parameters.

```python
def batch_run(self, 
              feature_name: str,
              param_list: List[Dict[str, Any]],
              max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
    """Execute feature in batch mode.
    
    Args:
        feature_name: Name of the feature
        param_list: List of parameter dictionaries
        max_workers: Maximum parallel workers
        
    Returns:
        List of results in the same order as param_list
    """

# Example
params = [
    {'text': 'I love this product!'},
    {'text': 'This is terrible'},
    {'text': 'It works okay'}
]
results = agi.batch_run('text_sentiment_analysis', params)
```

##### arun()
Asynchronous feature execution.

```python
async def arun(self, 
               feature_name: str,
               **kwargs) -> Dict[str, Any]:
    """Execute feature asynchronously."""

# Example
import asyncio

async def process_texts():
    tasks = [
        agi.arun('text_sentiment_analysis', text="Text 1"),
        agi.arun('text_sentiment_analysis', text="Text 2"),
        agi.arun('text_sentiment_analysis', text="Text 3")
    ]
    results = await asyncio.gather(*tasks)
    return results
```

##### list_features()
Get available features with optional filtering.

```python
def list_features(self, 
                  category: Optional[str] = None,
                  tag: Optional[str] = None,
                  search: Optional[str] = None) -> List[str]:
    """List available features.
    
    Args:
        category: Filter by category
        tag: Filter by tag
        search: Search in feature names and descriptions
        
    Returns:
        List of feature names
    """

# Examples
all_features = agi.list_features()
nlp_features = agi.list_features(category='nlp')
sentiment_features = agi.list_features(search='sentiment')
```

##### get_feature_info()
Get detailed information about a specific feature.

```python
def get_feature_info(self, feature_name: str) -> Dict[str, Any]:
    """Get feature information.
    
    Args:
        feature_name: Name of the feature
        
    Returns:
        Dictionary with feature metadata
    """

# Example
info = agi.get_feature_info('text_sentiment_analysis')
print(info['description'])
print(info['parameters'])
print(info['category'])
print(info['tags'])
```

##### Pipeline Support
Create and execute feature pipelines.

```python
def create_pipeline(self, steps: List[Tuple[str, Dict]]) -> Pipeline:
    """Create a feature pipeline.
    
    Args:
        steps: List of (feature_name, parameters) tuples
        
    Returns:
        Pipeline object
    """

# Example
pipeline = agi.create_pipeline([
    ('text_cleaner', {'remove_punctuation': True}),
    ('text_sentiment_analysis', {}),
    ('data_confidence_filter', {'min_confidence': 0.8})
])

result = pipeline.run(text="Messy input text!!!")
```

### Feature Categories API

#### FeatureRegistry

Access to the feature registry for advanced operations.

```python
from openagi.core import FeatureRegistry

registry = FeatureRegistry()

# Register custom feature
registry.register(custom_feature)

# Get feature by name
feature = registry.get('text_sentiment_analysis')

# List features by category
nlp_features = registry.list_by_category('nlp')
```

#### AIFeature Base Class

Base class for implementing custom features.

```python
from openagi.core import AIFeature

class CustomSentimentAnalysis(AIFeature):
    """Custom sentiment analysis feature."""
    
    def __init__(self):
        super().__init__(
            name="custom_sentiment_analysis",
            category="nlp",
            description="Custom sentiment analysis with domain adaptation"
        )
        self.tags = ["sentiment", "text", "custom"]
    
    def execute(self, text: str, domain: str = "general") -> Dict[str, Any]:
        """Execute sentiment analysis.
        
        Args:
            text: Input text
            domain: Domain for adaptation
            
        Returns:
            Sentiment analysis results
        """
        # Implementation here
        return {
            'sentiment': 'positive',
            'confidence': 0.95,
            'domain': domain
        }
    
    def validate_params(self, **kwargs) -> None:
        """Validate input parameters."""
        if 'text' not in kwargs:
            raise ValueError("'text' parameter is required")
        if not isinstance(kwargs['text'], str):
            raise TypeError("'text' must be a string")
```

### Configuration API

#### Settings Management

```python
from openagi.config import Settings

# Load settings
settings = Settings.load('config.yaml')

# Access configuration
nlp_config = settings.nlp
api_config = settings.api

# Update settings
settings.update({
    'nlp': {
        'max_text_length': 5000
    }
})

# Save settings
settings.save('updated_config.yaml')
```

#### Environment Configuration

```python
from openagi.config import env_config

# Get environment-based configuration
config = env_config()

# Override with environment variables
# OPENAGI_LOG_LEVEL=DEBUG
# OPENAGI_CACHE_ENABLED=false
```

### Caching API

#### Cache Management

```python
from openagi.cache import CacheManager

cache = CacheManager()

# Manual cache operations
cache.set('key', value, ttl=3600)
cached_value = cache.get('key')
cache.delete('key')
cache.clear()

# Cache statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
print(f"Cache size: {stats['size']}")
```

### Monitoring API

#### Metrics Collection

```python
from openagi.monitoring import MetricsCollector

metrics = MetricsCollector()

# Get execution metrics
execution_metrics = metrics.get_execution_metrics()
feature_metrics = metrics.get_feature_metrics('text_sentiment_analysis')

# Performance metrics
performance = metrics.get_performance_metrics()
print(f"Average execution time: {performance['avg_execution_time']}")
print(f"Features per second: {performance['features_per_second']}")
```

## 🌐 REST API

OpenAGI provides a REST API for language-agnostic access.

### Starting the API Server

```bash
# Start development server
openagi serve --host 0.0.0.0 --port 8000 --reload

# Start production server
openagi serve --host 0.0.0.0 --port 8000 --workers 4
```

### Authentication

```python
# API Key authentication
headers = {
    'Authorization': 'Bearer your_api_key',
    'Content-Type': 'application/json'
}
```

### Endpoints

#### POST /api/v1/features/{feature_name}/execute

Execute a feature via REST API.

```bash
curl -X POST "http://localhost:8000/api/v1/features/text_sentiment_analysis/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "I love this product!"
     }'
```

Response:
```json
{
  "status": "success",
  "result": {
    "sentiment": "positive",
    "confidence": 0.92
  },
  "execution_time": 0.15,
  "feature_name": "text_sentiment_analysis"
}
```

#### GET /api/v1/features

List available features.

```bash
curl "http://localhost:8000/api/v1/features?category=nlp&limit=10"
```

Response:
```json
{
  "features": [
    {
      "name": "text_sentiment_analysis",
      "category": "nlp",
      "description": "Analyze text sentiment",
      "tags": ["sentiment", "text", "analysis"]
    }
  ],
  "total": 234,
  "page": 1,
  "limit": 10
}
```

#### GET /api/v1/features/{feature_name}

Get feature information.

```bash
curl "http://localhost:8000/api/v1/features/text_sentiment_analysis"
```

Response:
```json
{
  "name": "text_sentiment_analysis",
  "category": "nlp",
  "description": "Analyze sentiment in text",
  "parameters": {
    "text": {
      "type": "string",
      "description": "Input text to analyze",
      "required": true
    }
  },
  "tags": ["sentiment", "text"],
  "version": "1.0.0"
}
```

#### POST /api/v1/batch/execute

Batch feature execution.

```bash
curl -X POST "http://localhost:8000/api/v1/batch/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "feature_name": "text_sentiment_analysis",
       "requests": [
         {"text": "I love this!"},
         {"text": "This is terrible"},
         {"text": "It works okay"}
       ]
     }'
```

#### WebSocket API

Real-time feature execution via WebSocket.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function() {
    // Send feature execution request
    ws.send(JSON.stringify({
        feature_name: 'text_sentiment_analysis',
        parameters: {
            text: 'Real-time sentiment analysis!'
        }
    }));
};

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log('Result:', result);
};
```

## 🖥️ CLI Interface

### Command Structure

```bash
openagi [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS]
```

### Global Options

```bash
--config PATH          Configuration file path
--log-level LEVEL      Logging level (DEBUG, INFO, WARNING, ERROR)
--no-cache            Disable caching
--timeout SECONDS     Default timeout for operations
--help                Show help message
--version             Show version information
```

### Commands

#### info
Show platform information.

```bash
openagi info [--verbose]
```

#### list-features
List available features.

```bash
openagi list-features [OPTIONS]

Options:
  --category TEXT     Filter by category
  --tag TEXT         Filter by tag
  --search TEXT      Search in names and descriptions
  --limit INTEGER    Limit number of results
  --format FORMAT    Output format (table, json, yaml)
```

#### run
Execute a feature.

```bash
openagi run FEATURE_NAME [OPTIONS]

Options:
  --params JSON      Feature parameters as JSON
  --input-file PATH  Input file path
  --output-file PATH Output file path
  --timeout INTEGER  Execution timeout
  --verbose         Verbose output
```

#### batch-run
Execute features in batch mode.

```bash
openagi batch-run FEATURE_NAME [OPTIONS]

Options:
  --input-dir PATH   Input directory
  --params-file PATH Parameters file (JSON/YAML)
  --output-dir PATH  Output directory
  --workers INTEGER  Number of parallel workers
```

#### serve
Start the REST API server.

```bash
openagi serve [OPTIONS]

Options:
  --host TEXT        Host address (default: 127.0.0.1)
  --port INTEGER     Port number (default: 8000)
  --workers INTEGER  Number of worker processes
  --reload          Auto-reload on code changes
  --ssl-cert PATH   SSL certificate file
  --ssl-key PATH    SSL key file
```

#### interactive
Start interactive mode.

```bash
openagi interactive [--config PATH]
```

#### diagnose
Run system diagnostics.

```bash
openagi diagnose [--full]
```

### Configuration Commands

#### config
Manage configuration.

```bash
# Show current configuration
openagi config show

# Set configuration value
openagi config set nlp.max_text_length 5000

# Get configuration value  
openagi config get cache.enabled

# Reset to defaults
openagi config reset
```

#### cache
Manage cache.

```bash
# Show cache statistics
openagi cache stats

# Clear cache
openagi cache clear

# Configure cache
openagi cache config --size 2GB --ttl 7200
```

## ⚠️ Error Handling

### Exception Hierarchy

```python
OpenAGIError                    # Base exception
├── ConfigurationError          # Configuration issues
├── FeatureError               # Feature-related errors
│   ├── FeatureNotFoundError   # Feature doesn't exist
│   ├── FeatureExecutionError  # Execution failed
│   └── ParameterError         # Invalid parameters
├── ModelError                 # AI model errors
│   ├── ModelNotFoundError     # Model not available
│   ├── ModelLoadError         # Model loading failed
│   └── ModelPredictionError   # Prediction failed
├── CacheError                 # Cache-related errors
├── APIError                   # API-related errors
│   ├── AuthenticationError    # Authentication failed
│   ├── RateLimitError        # Rate limit exceeded
│   └── TimeoutError          # Request timeout
└── ValidationError            # Input validation errors
```

### Error Response Format

```python
# Python API
try:
    result = agi.run('text_sentiment_analysis', text="")
except ParameterError as e:
    print(f"Parameter error: {e}")
    print(f"Error code: {e.code}")
    print(f"Details: {e.details}")
```

REST API error response:
```json
{
  "error": {
    "type": "ParameterError",
    "message": "Required parameter 'text' is missing",
    "code": "MISSING_PARAMETER",
    "details": {
      "parameter": "text",
      "feature": "text_sentiment_analysis"
    }
  },
  "request_id": "req_123456789"
}
```

### Error Handling Best Practices

```python
from openagi import OpenAGI, OpenAGIError
import logging

logger = logging.getLogger(__name__)

def safe_feature_execution(agi, feature_name, **params):
    """Safely execute a feature with comprehensive error handling."""
    try:
        result = agi.run(feature_name, **params)
        return {
            'success': True,
            'result': result
        }
    except ParameterError as e:
        logger.warning(f"Parameter error in {feature_name}: {e}")
        return {
            'success': False,
            'error': 'parameter_error',
            'message': str(e)
        }
    except FeatureExecutionError as e:
        logger.error(f"Execution error in {feature_name}: {e}")
        return {
            'success': False,
            'error': 'execution_error',
            'message': str(e)
        }
    except TimeoutError as e:
        logger.error(f"Timeout in {feature_name}: {e}")
        return {
            'success': False,
            'error': 'timeout',
            'message': 'Feature execution timed out'
        }
    except OpenAGIError as e:
        logger.error(f"OpenAGI error in {feature_name}: {e}")
        return {
            'success': False,
            'error': 'openagi_error',
            'message': str(e)
        }
    except Exception as e:
        logger.exception(f"Unexpected error in {feature_name}: {e}")
        return {
            'success': False,
            'error': 'unexpected_error',
            'message': 'An unexpected error occurred'
        }
```

## 🔧 Advanced Usage

### Custom Model Integration

```python
from openagi.models import BaseModel

class CustomModel(BaseModel):
    """Custom AI model integration."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
    
    def load(self):
        """Load the model."""
        # Implementation here
        pass
    
    def predict(self, inputs):
        """Make predictions."""
        # Implementation here
        pass
    
    def unload(self):
        """Unload the model to free memory."""
        # Implementation here
        pass

# Register custom model
agi.register_model('custom_sentiment', CustomModel('path/to/model'))
```

### Plugin System

```python
from openagi.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    """Custom OpenAGI plugin."""
    
    def on_feature_start(self, feature_name, params):
        """Called before feature execution."""
        print(f"Starting {feature_name} with {params}")
    
    def on_feature_complete(self, feature_name, result):
        """Called after successful feature execution."""
        print(f"Completed {feature_name}: {result}")
    
    def on_feature_error(self, feature_name, error):
        """Called when feature execution fails."""
        print(f"Error in {feature_name}: {error}")

# Register plugin
agi.register_plugin(CustomPlugin())
```

### Performance Monitoring

```python
from openagi.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

# Track execution time
with monitor.track('text_sentiment_analysis'):
    result = agi.run('text_sentiment_analysis', text="Test")

# Get performance report
report = monitor.get_report()
print(f"Average execution time: {report['avg_time']}")
print(f"Total executions: {report['total_executions']}")
```

---

For more examples and detailed usage, see the [User Guide](User-Guide.md) and [Examples](Examples.md).