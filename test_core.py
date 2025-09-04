#!/usr/bin/env python3
"""
Simple test script for OpenAGI core functionality without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_directives():
    """Test core directives module."""
    try:
        from openagi.core_directives import CORE_DIRECTIVES, get_directives_prompt
        print("✅ Core directives loaded successfully")
        print(f"   - Found {len(CORE_DIRECTIVES)} directives")
        print(f"   - Prompt length: {len(get_directives_prompt())} characters")
        return True
    except Exception as e:
        print(f"❌ Core directives failed: {e}")
        return False

def test_memory_system():
    """Test memory system (might fail without chromadb)."""
    try:
        from openagi.agent.memory import MemoryManager
        print("✅ Memory system import successful")
        return True
    except Exception as e:
        print(f"⚠️  Memory system failed (expected without chromadb): {e}")
        return False

def test_tool_base():
    """Test tool base class."""
    try:
        from openagi.tools.base import BaseTool
        print("✅ Tool base class loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Tool base class failed: {e}")
        return False

def test_helios_components():
    """Test Helios components."""
    try:
        from openagi.helios.server import HeliosServer
        from openagi.helios.client import HeliosClient
        print("✅ Helios components loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Helios components failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing OpenAGI Core Components (without dependencies)")
    print("=" * 60)
    
    tests = [
        test_core_directives,
        test_memory_system,
        test_tool_base,
        test_helios_components
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All core components working! Ready for full installation.")
    elif passed > total // 2:
        print("✨ Core architecture is solid. Install dependencies to unlock full power.")
    else:
        print("⚠️  Some issues detected. Check imports and file structure.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)