# Installation Guide

This guide provides comprehensive installation instructions for OpenAGI across different platforms and use cases.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 8GB (16GB+ recommended for ML features)
- **Storage**: 5GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Internet**: Required for downloading models and dependencies

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 16GB+ (32GB for heavy ML workloads)
- **Storage**: 20GB+ free space (models and cache)
- **GPU**: NVIDIA GPU with CUDA support (optional, for GPU acceleration)
- **CPU**: Multi-core processor (8+ cores recommended)

## 🚀 Installation Methods

### Method 1: Quick Install (Recommended)

The fastest way to get started:

```bash
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Install with pip
pip install -e .
```

### Method 2: Development Install

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install in development mode with dev dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Method 3: From PyPI (Coming Soon)

```bash
# Install from PyPI (when available)
pip install openagi
```

## 🐳 Docker Installation

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Start with Docker Compose
docker-compose up -d
```

### Manual Docker Build

```bash
# Build Docker image
docker build -t openagi .

# Run container
docker run -it --rm -p 8000:8000 openagi
```

### Docker with GPU Support

```bash
# Build with GPU support
docker build -t openagi:gpu -f Dockerfile.gpu .

# Run with GPU access
docker run --gpus all -it --rm -p 8000:8000 openagi:gpu
```

## 🖥️ Platform-Specific Instructions

### Windows

#### Prerequisites
```powershell
# Install Python 3.8+ from python.org
# Install Git from git-scm.com

# Verify installations
python --version
git --version
```

#### Installation
```powershell
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install OpenAGI
pip install -e .
```

#### Windows-Specific Dependencies
Some features may require additional Windows-specific dependencies:

```powershell
# For audio processing
pip install python-sounddevice

# For computer vision with DirectML
pip install tensorflow-directml
```

### macOS

#### Prerequisites
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git

# Verify installations
python3 --version
git --version
```

#### Installation
```bash
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install OpenAGI
pip install -e .
```

#### macOS-Specific Notes
- Use `python3` and `pip3` instead of `python` and `pip`
- For M1/M2 Macs, some ML libraries may require ARM-specific builds
- Install Xcode Command Line Tools if prompted

### Linux (Ubuntu/Debian)

#### Prerequisites
```bash
# Update package list
sudo apt update

# Install Python, pip, and Git
sudo apt install python3 python3-pip python3-venv git

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev

# Verify installations
python3 --version
git --version
```

#### Installation
```bash
# Clone repository
git clone https://github.com/VIIICORP/OpenAGI.git
cd OpenAGI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install OpenAGI
pip install -e .
```

#### Linux-Specific Dependencies
```bash
# For audio processing
sudo apt install portaudio19-dev

# For computer vision
sudo apt install libopencv-dev

# For ML with GPU support
sudo apt install nvidia-cuda-toolkit
```

### CentOS/RHEL/Fedora

#### Prerequisites
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip git gcc openssl-devel libffi-devel python3-devel

# Fedora
sudo dnf install python3 python3-pip git gcc openssl-devel libffi-devel python3-devel
```

## 🎯 GPU Support Setup

### NVIDIA GPU (CUDA)

#### Install CUDA Toolkit
```bash
# Download and install CUDA from nvidia.com
# Verify CUDA installation
nvcc --version
nvidia-smi
```

#### Install GPU-Enabled Dependencies
```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install TensorFlow with GPU support
pip install tensorflow-gpu

# Install OpenAGI with GPU extras
pip install -e .[gpu]
```

### AMD GPU (ROCm)

```bash
# Install ROCm (Linux only)
# Follow AMD ROCm installation guide

# Install PyTorch with ROCm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
```

### Apple Silicon (M1/M2)

```bash
# Install TensorFlow Metal
pip install tensorflow-metal

# TensorFlow will automatically use Metal Performance Shaders
```

## 🔧 Configuration

### Basic Configuration

Create `config.yaml`:

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

computer_vision:
  default_image_format: "RGB"
  max_image_size: [1920, 1080]

machine_learning:
  default_random_state: 42
  cross_validation_folds: 5
```

### Environment Variables

```bash
# Set OpenAGI configuration path
export OPENAGI_CONFIG_PATH="/path/to/config.yaml"

# Set cache directory
export OPENAGI_CACHE_DIR="/path/to/cache"

# Set log level
export OPENAGI_LOG_LEVEL="INFO"
```

## ✅ Verify Installation

### Basic Verification

```bash
# Check OpenAGI installation
openagi info

# List available features
openagi list-features --limit 5

# Run a simple test
echo "Hello world" | openagi run text_tokenizer
```

### Python API Verification

```python
from openagi import OpenAGI

# Initialize OpenAGI
agi = OpenAGI()

# List categories
categories = agi.list_categories()
print(f"Available categories: {categories}")

# Get feature count
feature_count = agi.count_features()
print(f"Total features: {feature_count}")
```

### Comprehensive Test

```bash
# Run the test suite
pytest tests/

# Run quick smoke tests
openagi test --quick

# Check system diagnostics
openagi diagnose
```

## 🐛 Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If using multiple Python versions
python3.10 --version
python3.10 -m pip install -e .
```

#### Permission Issues (Linux/macOS)
```bash
# Use --user flag for local installation
pip install --user -e .

# Or fix permissions
sudo chown -R $USER ~/.local/
```

#### Dependency Conflicts
```bash
# Create clean environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install -e .
```

#### Windows Path Issues
```powershell
# Add Python to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Python39\;C:\Python39\Scripts\", "User")
```

### Performance Issues

#### Slow Feature Loading
```yaml
# In config.yaml
enable_caching: true
auto_load_features: false  # Load features on demand
```

#### Memory Issues
```yaml
# Reduce concurrent features
max_concurrent_features: 5

# Limit model cache
cache:
  max_size: "512MB"
```

### GPU Issues

#### CUDA Not Found
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### GPU Memory Issues
```python
# In your code, limit GPU memory
import torch
torch.cuda.set_per_process_memory_fraction(0.5)
```

## 🔄 Updating OpenAGI

### Git Update
```bash
cd OpenAGI
git pull origin main
pip install -e .
```

### Dependency Updates
```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Update specific packages
pip install --upgrade transformers torch tensorflow
```

## 🗑️ Uninstallation

### Remove OpenAGI
```bash
# Uninstall package
pip uninstall openagi

# Remove cache and config (optional)
rm -rf ~/.openagi
```

### Complete Cleanup
```bash
# Remove virtual environment
rm -rf venv/

# Remove repository
rm -rf OpenAGI/
```

## 📞 Getting Help

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](Troubleshooting.md)
2. Search [GitHub Issues](https://github.com/VIIICORP/OpenAGI/issues)
3. Ask in [GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions)
4. Email: contact@viiicorp.com

---

**Installation complete!** 🎉 Ready to explore OpenAGI? Check out the [Getting Started Guide](Getting-Started.md).