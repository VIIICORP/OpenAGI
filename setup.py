#!/usr/bin/env python3
"""
OpenAGI Setup Script

Automated setup and installation for OpenAGI.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the OpenAGI setup banner."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                   🌟 OpenAGI Setup 🌟                         ║
║              Setting up your AGI environment...                ║
╚════════════════════════════════════════════════════════════════╝
""")

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "agent_memory",
        "logs",
        "output"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def check_optional_dependencies():
    """Check for optional dependencies and provide guidance."""
    print("\n🔍 Checking optional dependencies...")
    
    optional_deps = {
        "torch": "PyTorch (for voice interface)",
        "whisper": "OpenAI Whisper (for speech recognition)",
        "TTS": "Coqui TTS (for speech synthesis)",
        "chromadb": "ChromaDB (for memory system)"
    }
    
    missing = []
    
    for package, description in optional_deps.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚠️  {package} - {description} (will be installed)")
            missing.append(package)
    
    return missing

def test_installation():
    """Test the installation by importing core modules."""
    print("\n🧪 Testing installation...")
    
    try:
        from openagi.core_directives import CORE_DIRECTIVES
        from openagi.agent.engine import AgentEngine
        from openagi.agent.memory import MemoryManager
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def show_next_steps():
    """Show next steps after installation."""
    print("""
🎉 OpenAGI Setup Complete!

Next steps:
1. Start OpenAGI:
   python main.py

2. Open the Helios dashboard:
   http://localhost:8765

3. Try some goals:
   - "Search for the latest AI research"
   - "Create a simple Python calculator"
   - "Generate a musical melody"

4. Read the documentation:
   - README.md for detailed instructions
   - VISION.md for the OpenAGI philosophy

🌟 Welcome to the future of HUAIMKIND!
""")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the OpenAGI root directory")
        sys.exit(1)
    
    # Check optional dependencies first
    missing = check_optional_dependencies()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Installation test failed, but you can still try running OpenAGI")
        print("   Some features may not be available due to missing dependencies")
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()