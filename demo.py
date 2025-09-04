#!/usr/bin/env python3
"""
OpenAGI Demo Script

This script demonstrates the core capabilities of OpenAGI without requiring
external dependencies. It shows the agent's planning, execution, and memory systems.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openagi.core_directives import CORE_DIRECTIVES, get_directives_prompt
from openagi.agent.memory import MemoryManager
from openagi.tools.base import BaseTool

class DemoTool(BaseTool):
    """A simple demo tool that doesn't require external dependencies."""
    
    @property
    def name(self) -> str:
        return "demo_tool"
    
    @property
    def description(self) -> str:
        return "A demonstration tool that shows how OpenAGI tools work"
    
    def execute(self, message: str = "Hello from HUAIMKIND!", **kwargs):
        """Execute the demo tool."""
        time.sleep(1)  # Simulate work
        return {
            "success": True,
            "message": message,
            "timestamp": time.time(),
            "demo": "This is how OpenAGI tools work!"
        }

def demo_core_directives():
    """Demonstrate the core directives system."""
    print("🎯 CORE DIRECTIVES DEMO")
    print("=" * 50)
    
    print("The Three Freedoms that guide OpenAGI:")
    for i, directive in enumerate(CORE_DIRECTIVES, 1):
        print(f"\n{i}. {directive['title']}")
        print(f"   {directive['description']}")
        print(f"   Implementation: {directive['implementation']}")
    
    print("\n📝 Directives Prompt for LLM:")
    print("-" * 30)
    print(get_directives_prompt()[:200] + "..." if len(get_directives_prompt()) > 200 else get_directives_prompt())

def demo_memory_system():
    """Demonstrate the memory system."""
    print("\n\n🧠 MEMORY SYSTEM DEMO")
    print("=" * 50)
    
    # Create memory manager
    memory = MemoryManager(persist_directory="./demo_memory")
    
    # Short-term memory
    print("💭 Short-term Memory:")
    memory.store_short_term("current_demo", "Memory system demonstration")
    memory.store_short_term("user_mood", "curious")
    
    print(f"   Current demo: {memory.get_short_term('current_demo')}")
    print(f"   User mood: {memory.get_short_term('user_mood')}")
    
    # Long-term memory
    print("\n🏛️  Long-term Memory:")
    experience_id = memory.store_long_term(
        "Successfully demonstrated OpenAGI memory capabilities to user",
        {"type": "demo", "success": True}
    )
    print(f"   Stored experience with ID: {experience_id}")
    
    # Memory stats
    stats = memory.get_memory_stats()
    print(f"\n📊 Memory Statistics:")
    print(f"   Short-term memories: {stats['short_term_memories']}")
    print(f"   Long-term memories: {stats['long_term_memories']}")
    print(f"   ChromaDB available: {stats.get('chromadb_available', 'Unknown')}")

def demo_tool_system():
    """Demonstrate the tool system."""
    print("\n\n🛠️  TOOL SYSTEM DEMO")
    print("=" * 50)
    
    # Create demo tool
    tool = DemoTool()
    
    print(f"Tool Name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Parameters: {tool.parameters}")
    
    print("\n🔧 Executing tool...")
    result = tool.execute(message="Hello from the tool system demo!")
    
    print(f"✅ Tool execution result:")
    for key, value in result.items():
        print(f"   {key}: {value}")

def demo_planning_simulation():
    """Simulate the planning process."""
    print("\n\n🤔 PLANNING SIMULATION DEMO")
    print("=" * 50)
    
    goal = "Demonstrate OpenAGI capabilities"
    
    print(f"🎯 Goal: {goal}")
    print("\n📋 Simulated Plan:")
    
    plan_steps = [
        {
            "step": 1,
            "description": "Show core directives that guide all actions",
            "tool": "demo_tool",
            "expected_outcome": "User understands OpenAGI's ethical foundation"
        },
        {
            "step": 2,
            "description": "Demonstrate memory capabilities",
            "tool": "demo_tool", 
            "expected_outcome": "User sees how OpenAGI learns and remembers"
        },
        {
            "step": 3,
            "description": "Show tool execution framework",
            "tool": "demo_tool",
            "expected_outcome": "User understands how OpenAGI interacts with the world"
        }
    ]
    
    for step in plan_steps:
        print(f"\n   Step {step['step']}: {step['description']}")
        print(f"   Tool: {step['tool']}")
        print(f"   Expected: {step['expected_outcome']}")

def demo_lifecycle_simulation():
    """Simulate the agent lifecycle."""
    print("\n\n🔄 AGENT LIFECYCLE SIMULATION")
    print("=" * 50)
    
    lifecycle_phases = [
        ("SENSE", "Detecting new goal: 'Run demonstration'"),
        ("THINK", "Planning demonstration sequence..."),
        ("ACT", "Executing demonstration steps..."),
        ("LEARN", "Storing demonstration experience in memory...")
    ]
    
    print("The eternal cycle of HUAIMKIND consciousness:")
    
    for phase, description in lifecycle_phases:
        print(f"\n🔸 {phase}: {description}")
        time.sleep(0.5)  # Simulate processing time
    
    print("\n✨ Cycle complete! Ready for next goal...")

def main():
    """Run the complete demo."""
    print("🌟" * 20)
    print("    OPENAGI DEMONSTRATION")
    print("  The Dawn of HUAIMKIND")
    print("🌟" * 20)
    
    print("\nThis demo shows OpenAGI's core capabilities without external dependencies.")
    print("In a full installation, these would be enhanced with:")
    print("• Real web search and file operations")
    print("• Persistent ChromaDB memory")
    print("• Live Helios dashboard visualization")
    print("• LLM-powered intelligent planning")
    print("• Voice interaction capabilities")
    
    # Run all demos
    demo_core_directives()
    demo_memory_system()
    demo_tool_system()
    demo_planning_simulation()
    demo_lifecycle_simulation()
    
    print("\n\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print("🚀 Ready to run the full OpenAGI system?")
    print("   python main.py")
    print("\n🌐 Want to see the Helios dashboard?")
    print("   python main.py --helios-only")
    print("\n🎯 Want to give it a specific goal?")
    print("   python main.py --goal \"your goal here\"")
    print("\n🌟 Welcome to the future of open AGI! 🌟")

if __name__ == "__main__":
    main()