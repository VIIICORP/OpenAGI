#!/bin/bash

# OpenAGI Start Script
# Quick start script for the OpenAGI platform

echo "🤖 Starting OpenAGI Platform..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    pip install -e .
    touch venv/installed
fi

# Check if config file exists
if [ ! -f "config.yaml" ]; then
    echo "⚙️  No config.yaml found, using defaults"
fi

echo "✅ Environment ready!"
echo ""

# Show available options
echo "Available options:"
echo "  1. Run basic example"
echo "  2. Start CLI interface"
echo "  3. Run platform demo"
echo "  4. Run tests"
echo "  5. Python shell with OpenAGI loaded"
echo ""

read -p "Choose an option (1-5): " choice

case $choice in
    1)
        echo "🚀 Running basic example..."
        python examples/basic_usage.py
        ;;
    2)
        echo "🖥️  Starting CLI interface..."
        python -m openagi.cli --help
        echo ""
        echo "Try: python -m openagi.cli info"
        ;;
    3)
        echo "🎬 Running platform demo..."
        python -m openagi.cli demo
        ;;
    4)
        echo "🧪 Running tests..."
        if command -v pytest &> /dev/null; then
            pytest tests/ -v
        else
            echo "Installing pytest..."
            pip install pytest pytest-cov
            pytest tests/ -v
        fi
        ;;
    5)
        echo "🐍 Starting Python shell with OpenAGI..."
        python -c "
import sys
print('OpenAGI Platform Shell')
print('======================')
print('OpenAGI modules are available.')
print('Try: from openagi import OpenAGI')
print('     platform = OpenAGI()')
print('     platform.get_platform_stats()')
print('')
from openagi import OpenAGI
platform = OpenAGI()
print(f'Platform loaded with {platform.get_platform_stats()[\"total_features\"]} features')
print('')
" && python
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✨ Done! Visit the README.md for more information."

# Deactivate virtual environment
deactivate