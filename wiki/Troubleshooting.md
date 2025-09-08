# Troubleshooting Guide

Common issues and solutions for OpenAGI users.

## 📋 Quick Diagnostic

Before diving into specific issues, run these commands to gather system information:

```bash
# Check OpenAGI installation
openagi info

# Check system diagnostics
openagi diagnose

# Check Python environment
python --version
pip --version

# Check OpenAGI version
python -c "import openagi; print(openagi.__version__)"
```

## 🚨 Installation Issues

### Python Version Problems

**Issue:** `Python version not supported` or `Requires Python 3.8+`

**Solutions:**
```bash
# Check Python version
python --version

# If using multiple Python versions
python3.10 --version
python3.10 -m pip install -e .

# Use pyenv for version management (Linux/macOS)
pyenv install 3.10.0
pyenv global 3.10.0
```

### Dependency Installation Failures

**Issue:** `Failed building wheel` or `Microsoft Visual C++ required`

**Windows Solutions:**
```bash
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Install pre-compiled wheels
pip install --only-binary=all -e .
```

**Linux Solutions:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# Alpine
apk add build-base python3-dev
```

**macOS Solutions:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Or install via Homebrew
brew install python@3.10
```

### Memory Issues During Installation

**Issue:** `MemoryError` or `Killed` during pip install

**Solutions:**
```bash
# Increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Install without cache
pip install --no-cache-dir -e .

# Install dependencies one by one
pip install numpy pandas
pip install scikit-learn
pip install -e .
```

### Permission Errors

**Issue:** `Permission denied` or `Access is denied`

**Solutions:**
```bash
# Use user installation (recommended)
pip install --user -e .

# Fix permissions (Linux/macOS)
sudo chown -R $USER ~/.local/
sudo chown -R $USER ~/.cache/pip/

# Windows: Run as Administrator or use --user flag
```

## ⚡ Performance Issues

### Slow Feature Loading

**Issue:** Features take a long time to load or execute

**Diagnosis:**
```python
import time
from openagi import OpenAGI

agi = OpenAGI()

# Time feature loading
start = time.time()
result = agi.run('text_sentiment_analysis', text="test")
print(f"Execution time: {time.time() - start:.2f} seconds")
```

**Solutions:**

1. **Enable Caching:**
```yaml
# config.yaml
cache:
  enabled: true
  max_size: "2GB"
  ttl: 3600
```

2. **Preload Models:**
```python
agi = OpenAGI()
agi.preload_models(['text_sentiment_analysis', 'image_object_detection'])
```

3. **Use Lighter Models:**
```yaml
nlp:
  models:
    sentiment: "distilbert-base-uncased"  # Smaller, faster model
```

4. **Increase Timeout:**
```python
result = agi.run('feature_name', timeout=600, **params)
```

### Memory Usage Issues

**Issue:** High memory consumption or `OutOfMemoryError`

**Diagnosis:**
```python
import psutil
import os

# Check memory usage
process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")

# Monitor during execution
agi = OpenAGI()
print(f"Before: {process.memory_info().rss / 1024 / 1024:.2f} MB")
result = agi.run('text_sentiment_analysis', text="test")
print(f"After: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

**Solutions:**

1. **Limit Concurrent Features:**
```yaml
max_concurrent_features: 3
```

2. **Reduce Cache Size:**
```yaml
cache:
  max_size: "512MB"
```

3. **Use Batch Processing:**
```python
# Instead of individual calls
results = agi.batch_run('text_sentiment_analysis', param_list, max_workers=2)
```

4. **Clear Cache Periodically:**
```python
agi.clear_cache()
import gc
gc.collect()
```

### GPU Issues

**Issue:** GPU not detected or CUDA errors

**Diagnosis:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
```

**Solutions:**

1. **Install CUDA Toolkit:**
```bash
# Check NVIDIA driver
nvidia-smi

# Install CUDA (example for CUDA 11.8)
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

2. **Install GPU-enabled PyTorch:**
```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CPU-only (if GPU issues persist)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

3. **Configure GPU Usage:**
```yaml
# config.yaml
gpu:
  enabled: true
  memory_fraction: 0.7  # Use 70% of GPU memory
  allow_growth: true
```

## 🔧 Feature Execution Issues

### Feature Not Found Errors

**Issue:** `FeatureNotFoundError: 'feature_name' not found`

**Diagnosis:**
```python
from openagi import OpenAGI

agi = OpenAGI()

# List all available features
features = agi.list_features()
print(f"Total features: {len(features)}")

# Search for similar features
sentiment_features = agi.search_features('sentiment')
print(f"Sentiment features: {sentiment_features}")

# Check specific category
nlp_features = agi.list_features(category='nlp')
print(f"NLP features: {len(nlp_features)}")
```

**Solutions:**

1. **Check Feature Name:**
```python
# Feature names are case-sensitive
# ❌ Wrong
agi.run('Text_Sentiment_Analysis', text="test")

# ✅ Correct
agi.run('text_sentiment_analysis', text="test")
```

2. **Update Feature Registry:**
```python
agi.refresh_features()
```

3. **Install Missing Dependencies:**
```bash
# Some features require additional packages
pip install transformers  # For NLP features
pip install opencv-python  # For computer vision
pip install librosa  # For audio processing
```

### Parameter Validation Errors

**Issue:** `ParameterError: Invalid parameter` or `Required parameter missing`

**Diagnosis:**
```python
# Get feature information
info = agi.get_feature_info('text_sentiment_analysis')
print("Required parameters:", info.get('parameters', {}))
print("Example usage:", info.get('example', {}))
```

**Solutions:**

1. **Check Required Parameters:**
```python
# ❌ Missing required parameter
agi.run('text_sentiment_analysis')

# ✅ Provide required parameter
agi.run('text_sentiment_analysis', text="I love this!")
```

2. **Validate Parameter Types:**
```python
# ❌ Wrong type
agi.run('text_sentiment_analysis', text=123)

# ✅ Correct type
agi.run('text_sentiment_analysis', text="Hello world")
```

3. **Check Parameter Limits:**
```python
# Check configuration limits
print(agi.config.nlp.max_text_length)

# ❌ Text too long
long_text = "x" * 50000
agi.run('text_sentiment_analysis', text=long_text)

# ✅ Truncate or chunk text
text = long_text[:agi.config.nlp.max_text_length]
agi.run('text_sentiment_analysis', text=text)
```

### Timeout Errors

**Issue:** `TimeoutError: Feature execution timed out`

**Diagnosis:**
```python
import time

# Time the execution
start = time.time()
try:
    result = agi.run('slow_feature', **params)
    print(f"Success in {time.time() - start:.2f} seconds")
except TimeoutError:
    print(f"Timeout after {time.time() - start:.2f} seconds")
```

**Solutions:**

1. **Increase Timeout:**
```python
# Per execution
result = agi.run('slow_feature', timeout=600, **params)  # 10 minutes

# Global setting
agi = OpenAGI(feature_timeout=600)
```

2. **Optimize Input Size:**
```python
# For text features
text = text[:5000]  # Limit text length

# For image features
from PIL import Image
img = Image.open('large_image.jpg')
img = img.resize((800, 600))  # Reduce image size
```

3. **Use Async Execution:**
```python
import asyncio

async def process_features():
    tasks = [
        agi.arun('feature1', **params1),
        agi.arun('feature2', **params2)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## 🌐 API Server Issues

### Server Won't Start

**Issue:** `Address already in use` or `Permission denied`

**Diagnosis:**
```bash
# Check if port is in use
netstat -tulpn | grep :8000
# or
lsof -i :8000

# Check permissions
whoami
id
```

**Solutions:**

1. **Use Different Port:**
```bash
openagi serve --port 8080
```

2. **Kill Existing Process:**
```bash
# Find process using port
sudo lsof -t -i:8000

# Kill process
sudo kill -9 $(sudo lsof -t -i:8000)
```

3. **Use Sudo for Privileged Ports:**
```bash
# For ports < 1024
sudo openagi serve --port 80
```

### Connection Issues

**Issue:** `Connection refused` or `Cannot connect to API`

**Diagnosis:**
```bash
# Test local connection
curl http://localhost:8000/api/v1/health

# Check server logs
openagi serve --log-level DEBUG

# Test network connectivity
ping localhost
telnet localhost 8000
```

**Solutions:**

1. **Check Host Binding:**
```bash
# Bind to all interfaces
openagi serve --host 0.0.0.0 --port 8000

# Or specific IP
openagi serve --host 192.168.1.100 --port 8000
```

2. **Configure Firewall:**
```bash
# Ubuntu/Debian
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

3. **Check Docker Network (if using containers):**
```bash
docker network ls
docker inspect <container_name>
```

### Authentication Problems

**Issue:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**

1. **Configure API Keys:**
```yaml
# config.yaml
api:
  require_auth: true
  api_keys:
    - "your_secret_key_here"
```

2. **Include Auth Header:**
```python
import requests

headers = {
    'Authorization': 'Bearer your_secret_key_here',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/api/v1/features/text_sentiment_analysis/execute',
    headers=headers,
    json={'text': 'Hello world'}
)
```

## 📊 Data and Model Issues

### Model Download Failures

**Issue:** `ModelNotFoundError` or download timeouts

**Diagnosis:**
```python
# Check internet connectivity
import requests
try:
    response = requests.get('https://huggingface.co', timeout=10)
    print(f"HuggingFace accessible: {response.status_code == 200}")
except:
    print("No internet access or HuggingFace blocked")
```

**Solutions:**

1. **Manual Model Download:**
```python
from transformers import AutoModel, AutoTokenizer

# Download models manually
model_name = "distilbert-base-uncased"
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Save locally
model.save_pretrained('./models/distilbert')
tokenizer.save_pretrained('./models/distilbert')
```

2. **Use Local Models:**
```yaml
# config.yaml
nlp:
  models:
    sentiment: "./models/distilbert"
```

3. **Configure Proxy:**
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Data Format Issues

**Issue:** `ValidationError` or `UnsupportedFormatError`

**Solutions:**

1. **Text Data:**
```python
# Ensure proper encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Clean text
text = text.strip()
text = ''.join(char for char in text if ord(char) < 65536)  # Remove invalid Unicode
```

2. **Image Data:**
```python
from PIL import Image
import numpy as np

# Ensure proper format
img = Image.open('image.jpg')
img = img.convert('RGB')  # Ensure RGB format
img_array = np.array(img)

# Check dimensions
print(f"Image shape: {img_array.shape}")
```

3. **Audio Data:**
```python
import librosa

# Load audio with specific parameters
audio, sr = librosa.load('audio.wav', sr=22050, mono=True)
print(f"Audio shape: {audio.shape}, Sample rate: {sr}")
```

## 🔍 Debugging Techniques

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# OpenAGI debug mode
agi = OpenAGI(debug=True, log_level="DEBUG")
```

### Trace Feature Execution

```python
# Enable verbose output
result = agi.run('text_sentiment_analysis', text="test", verbose=True)

# Dry run (validate without execution)
dry_result = agi.dry_run('text_sentiment_analysis', text="test")
print(f"Validation result: {dry_result}")
```

### Monitor Resource Usage

```python
import psutil
import threading
import time

def monitor_resources():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        print(f"CPU: {cpu}%, Memory: {memory}%")
        time.sleep(1)

# Start monitoring in background
monitor_thread = threading.Thread(target=monitor_resources)
monitor_thread.daemon = True
monitor_thread.start()

# Run your code
result = agi.run('expensive_feature', **params)
```

## 📞 Getting Help

### Collect System Information

Before asking for help, collect this information:

```bash
# System info
uname -a
python --version
pip --version

# OpenAGI info
openagi info
openagi diagnose

# Package versions
pip list | grep -E "(torch|tensorflow|transformers|numpy|pandas)"

# Error logs
tail -n 50 ~/.openagi/logs/openagi.log
```

### Report Issues

When reporting bugs:

1. **Include system information** (output from above commands)
2. **Provide minimal reproduction example**
3. **Include full error traceback**
4. **Specify expected vs actual behavior**

### Community Resources

- **[GitHub Issues](https://github.com/VIIICORP/OpenAGI/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions)** - Community help
- **[FAQ](FAQ.md)** - Frequently asked questions
- **Email:** contact@viiicorp.com

---

**Still having issues?** Don't hesitate to reach out to the community or create a detailed issue report on GitHub.