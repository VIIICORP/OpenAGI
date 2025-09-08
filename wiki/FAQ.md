# Frequently Asked Questions (FAQ)

Common questions and answers about OpenAGI.

## 🔧 General Questions

### What is OpenAGI?

OpenAGI is a unified artificial intelligence platform that brings together over 14,000 AI features across multiple domains, making advanced AI capabilities accessible through a simple, consistent interface.

### How many features does OpenAGI have?

OpenAGI currently includes **14,000+ AI features** across 15 major categories:
- Natural Language Processing (2,000+ features)
- Computer Vision (2,500+ features)
- Machine Learning (2,000+ features)
- Audio Processing (1,000+ features)
- Data Analysis (1,500+ features)
- And 10 more categories with hundreds of features each

### Is OpenAGI free to use?

Yes, OpenAGI is open source and available under the Apache 2.0 License. You can use it freely for both personal and commercial projects.

### What programming languages does OpenAGI support?

OpenAGI is primarily built in Python and provides:
- **Python API** - Native Python interface
- **REST API** - Language-agnostic HTTP API
- **CLI** - Command-line interface
- **WebSocket API** - Real-time communication

## 📦 Installation and Setup

### What are the system requirements?

**Minimum requirements:**
- Python 3.8+
- 8GB RAM
- 5GB free storage
- Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

**Recommended:**
- Python 3.10+
- 16GB+ RAM
- 20GB+ storage
- GPU for ML features (optional)

### How do I install OpenAGI?

The simplest way is:
```bash
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI
pip install -e .
```

For detailed installation instructions, see the [Installation Guide](Installation.md).

### Why is the installation taking so long?

OpenAGI has many dependencies for its 14,000+ features. The installation may take 10-30 minutes depending on your internet speed and system. You can:
- Use a faster internet connection
- Install with `--no-cache-dir` flag
- Install only specific categories if you don't need all features

### Can I install OpenAGI without all dependencies?

Yes, you can install a minimal version and add features as needed:
```bash
pip install -e .[minimal]
```

Then install specific categories:
```bash
pip install -e .[nlp]
pip install -e .[computer_vision]
```

## 🚀 Usage Questions

### How do I list available features?

```python
from openagi import OpenAGI
agi = OpenAGI()

# List all features
all_features = agi.list_features()

# List by category
nlp_features = agi.list_features(category='nlp')

# Search features
sentiment_features = agi.search_features('sentiment')
```

### How do I execute a feature?

```python
# Basic execution
result = agi.run('text_sentiment_analysis', text="I love this!")

# With CLI
echo "I love this!" | openagi run text_sentiment_analysis
```

### How do I get help for a specific feature?

```python
# Get feature information
info = agi.get_feature_info('text_sentiment_analysis')
print(info['description'])
print(info['parameters'])
```

Or use CLI:
```bash
openagi help text_sentiment_analysis
```

### Can I use multiple features together?

Yes! You can chain features or create pipelines:

```python
# Manual chaining
text = "This is amazing!"
cleaned = agi.run('text_cleaner', text=text)
sentiment = agi.run('text_sentiment_analysis', text=cleaned)

# Pipeline
pipeline = agi.create_pipeline([
    ('text_cleaner', {}),
    ('text_sentiment_analysis', {})
])
result = pipeline.run(text="This is amazing!")
```

## ⚡ Performance Questions

### Why are features running slowly?

Several factors can affect performance:

1. **First run**: Models need to be downloaded and loaded
2. **Hardware**: Insufficient RAM or CPU
3. **Configuration**: Cache disabled or low timeouts

**Solutions:**
- Enable caching: `agi = OpenAGI(cache_enabled=True)`
- Preload models: `agi.preload_models(['feature_name'])`
- Use GPU: Install GPU versions of ML libraries
- Increase timeout: `agi.run('feature', timeout=600)`

### How can I improve performance?

1. **Enable caching**:
```yaml
# config.yaml
cache:
  enabled: true
  max_size: "2GB"
```

2. **Use GPU acceleration**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

3. **Preload models**:
```python
agi.preload_models(['text_sentiment_analysis', 'image_object_detection'])
```

4. **Batch processing**:
```python
results = agi.batch_run('text_sentiment_analysis', param_list)
```

### Can I run OpenAGI on GPU?

Yes! Install GPU-enabled dependencies:

```bash
# For NVIDIA GPUs
pip install -e .[gpu]

# For Apple Silicon
pip install tensorflow-metal
```

Configure GPU usage:
```yaml
# config.yaml
gpu:
  enabled: true
  memory_fraction: 0.8
```

## 🔧 Configuration Questions

### How do I configure OpenAGI?

Create a `config.yaml` file:

```yaml
# Basic configuration
logging_level: INFO
enable_caching: true
max_concurrent_features: 10

# Feature-specific settings
nlp:
  default_language: "en"
  max_text_length: 10000

computer_vision:
  max_image_size: [1920, 1080]
```

### Where should I put the configuration file?

OpenAGI looks for configuration in this order:
1. Path specified with `--config` flag
2. `OPENAGI_CONFIG_PATH` environment variable
3. `./config.yaml` in current directory
4. `~/.openagi/config.yaml` in home directory

### How do I change the cache directory?

Set the environment variable:
```bash
export OPENAGI_CACHE_DIR="/path/to/cache"
```

Or in configuration:
```yaml
cache:
  directory: "/path/to/cache"
```

## 🐛 Troubleshooting

### I'm getting "Feature not found" errors

1. **Check feature name**:
```python
# List available features
features = agi.list_features()
print(features)
```

2. **Check spelling**: Feature names are case-sensitive
3. **Install dependencies**: Some features require additional packages

### Features are timing out

Increase timeout values:
```python
# Per execution
result = agi.run('feature_name', timeout=600)  # 10 minutes

# Global configuration
agi = OpenAGI(feature_timeout=300)
```

### I'm getting memory errors

1. **Reduce concurrent features**:
```yaml
max_concurrent_features: 3
```

2. **Limit cache size**:
```yaml
cache:
  max_size: "512MB"
```

3. **Use smaller models**:
```yaml
nlp:
  models:
    sentiment: "distilbert-base-uncased"  # Smaller model
```

### GPU is not being detected

1. **Check CUDA installation**:
```bash
nvidia-smi
nvcc --version
```

2. **Install GPU libraries**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

3. **Verify GPU availability**:
```python
import torch
print(torch.cuda.is_available())
```

## 🔌 API Questions

### How do I start the REST API server?

```bash
# Development server
openagi serve --host 0.0.0.0 --port 8000 --reload

# Production server
openagi serve --host 0.0.0.0 --port 8000 --workers 4
```

### How do I authenticate API requests?

Set up API key authentication:
```python
headers = {
    'Authorization': 'Bearer your_api_key',
    'Content-Type': 'application/json'
}
```

### Can I use OpenAGI with other programming languages?

Yes! Use the REST API from any language:

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/features/text_sentiment_analysis/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'I love this!'})
});
```

**Java:**
```java
// Use any HTTP client library
// Example with OkHttp, Retrofit, etc.
```

**C#:**
```csharp
// Use HttpClient
var client = new HttpClient();
var json = JsonSerializer.Serialize(new { text = "I love this!" });
var response = await client.PostAsync(url, new StringContent(json));
```

## 🛠️ Development Questions

### How do I create custom features?

Extend the base feature class:

```python
from openagi.core import AIFeature

class MyCustomFeature(AIFeature):
    def __init__(self):
        super().__init__(
            name="my_custom_feature",
            category="custom",
            description="My custom AI feature"
        )
    
    def execute(self, **kwargs):
        # Your implementation here
        return {"result": "custom_output"}

# Register the feature
agi.register_feature(MyCustomFeature())
```

### How do I contribute to OpenAGI?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See the [Contributing Guide](../CONTRIBUTING.md) for details.

### Can I add my own AI models?

Yes! You can integrate custom models:

```python
from openagi.models import BaseModel

class MyCustomModel(BaseModel):
    def load(self):
        # Load your model
        pass
    
    def predict(self, inputs):
        # Make predictions
        pass

# Register the model
agi.register_model('my_model', MyCustomModel())
```

## 📊 Monitoring and Debugging

### How do I enable debug logging?

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in configuration
agi = OpenAGI(log_level="DEBUG")
```

### How do I monitor feature performance?

```python
# Get execution metrics
metrics = agi.get_metrics()
print(f"Total executions: {metrics['total_executions']}")
print(f"Average time: {metrics['avg_execution_time']}")

# Feature-specific metrics
feature_metrics = agi.get_feature_metrics('text_sentiment_analysis')
```

### How do I debug feature execution?

```python
# Dry run (validate without execution)
result = agi.dry_run('text_sentiment_analysis', text="test")

# Verbose execution
result = agi.run('text_sentiment_analysis', text="test", verbose=True)

# Debug mode
agi = OpenAGI(debug=True)
```

## 🔒 Security Questions

### Is it safe to use OpenAGI in production?

OpenAGI includes security features:
- Input validation and sanitization
- Rate limiting capabilities
- Error handling and logging
- Configurable timeouts

For production use:
1. Configure proper authentication
2. Set up rate limiting
3. Monitor resource usage
4. Keep dependencies updated

### How do I secure the API server?

1. **Enable authentication**:
```yaml
api:
  require_auth: true
  api_keys: ["your_secure_key"]
```

2. **Use HTTPS**:
```bash
openagi serve --ssl-cert cert.pem --ssl-key key.pem
```

3. **Configure CORS**:
```yaml
api:
  cors_origins: ["https://yourdomain.com"]
```

### How do I handle sensitive data?

1. **Use environment variables** for API keys
2. **Don't log sensitive data**
3. **Configure data retention policies**
4. **Use encryption for stored data**

## 📞 Support Questions

### Where can I get help?

- **Documentation**: This wiki and [User Guide](User-Guide.md)
- **GitHub Issues**: [Report bugs](https://github.com/VIIICORP/OpenAGI/issues)
- **Discussions**: [Community discussions](https://github.com/VIIICORP/OpenAGI/discussions)
- **Email**: contact@viiicorp.com

### How do I report a bug?

1. Check if it's already reported in [GitHub Issues](https://github.com/VIIICORP/OpenAGI/issues)
2. Provide minimal reproduction example
3. Include system information and error logs
4. Use appropriate issue template

### How do I request a new feature?

1. Check [existing feature requests](https://github.com/VIIICORP/OpenAGI/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. Create a new issue with:
   - Clear description of the feature
   - Use case and motivation
   - Proposed API or interface
   - Any relevant examples

### Is there a community forum?

Yes! Use [GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions) for:
- General questions
- Feature discussions  
- Sharing use cases
- Getting help from the community

---

**Didn't find your question?** Check the [Troubleshooting Guide](Troubleshooting.md) or ask in [GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions).