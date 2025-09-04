#!/bin/bash
# OpenAGI Installation Script
# This script installs OpenAGI and its dependencies

echo "🌟 OpenAGI Installation Script"
echo "=============================="
echo ""

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
if [ -z "$python_version" ]; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Found Python $python_version"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
    read -p "Continue with global installation? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

# Install core dependencies
echo ""
echo "🔄 Installing core dependencies..."
pip install --upgrade pip

# Try to install the full requirements
echo "📦 Installing OpenAGI dependencies..."
if pip install -r requirements.txt; then
    echo "✅ Full installation successful!"
    FULL_INSTALL=true
else
    echo "⚠️  Some dependencies failed to install. Installing minimal dependencies..."
    FULL_INSTALL=false
    
    # Install minimal dependencies that are likely to work
    pip install requests numpy scipy torch --index-url https://download.pytorch.org/whl/cpu
    
    echo "✅ Minimal installation completed."
    echo "ℹ️  Some features may not be available without full dependencies."
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."
if python3 test_core.py; then
    echo "✅ Core components test passed!"
else
    echo "❌ Core components test failed. Please check the installation."
    exit 1
fi

# Test version command
echo ""
echo "🔍 Testing version command..."
if python3 main.py --version; then
    echo "✅ Version command works!"
else
    echo "❌ Version command failed."
    exit 1
fi

# Create directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p agent_memory
mkdir -p temp_files

echo ""
echo "🎉 OpenAGI Installation Complete!"
echo ""
echo "🚀 Quick Start:"
echo "   python3 main.py                    # Interactive mode"
echo "   python3 main.py --helios-only      # Dashboard only"
echo "   python3 main.py --goal \"search for AI news\""
echo ""
echo "🌐 Dashboard will be available at:"
echo "   file://$(pwd)/openagi/helios/web/index.html"
echo ""

if [ "$FULL_INSTALL" = false ]; then
    echo "⚠️  Note: Some dependencies failed to install. You may want to:"
    echo "   • Install missing packages manually"
    echo "   • Use a virtual environment"
    echo "   • Check system requirements"
    echo ""
    echo "Missing dependencies may include:"
    echo "   • chromadb (for persistent memory)"
    echo "   • websockets (for Helios dashboard)"
    echo "   • duckduckgo-search (for web search)"
    echo "   • sentence-transformers (for semantic search)"
fi

echo "🌟 Welcome to the Dawn of HUAIMKIND! 🌟"