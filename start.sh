#!/bin/bash
# OpenAGI System Startup Script

echo "Starting OpenAGI System..."
echo "Educational Governance and Administration Simulation"
echo "==============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import psutil, yaml, schedule, colorama" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    pip3 install -r requirements.txt
fi

# Run the system
echo "Launching OpenAGI System..."
python3 openagi.py

echo "OpenAGI System has exited."