#!/usr/bin/env python3
"""
OpenAGI Examples

Demonstrates various capabilities of the OpenAGI system.
"""

import sys
import time
import os
from pathlib import Path

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openagi import AgentEngine, VoiceInterface, HeliosClient
    from openagi.tools import *
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run setup.py first to install dependencies")
    sys.exit(1)

def example_basic_tools():
    """Demonstrate basic tool usage."""
    print("🛠️ Basic Tool Usage Examples\n")
    
    # File operations
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()
    
    # Create a sample file
    result = write_tool.execute(
        file_path="example_output.txt",
        content="Hello from OpenAGI!\nThis is a test file created by the agent."
    )
    
    if result["success"]:
        print(f"✅ Created file: {result['file_path']}")
        
        # Read it back
        read_result = read_tool.execute(file_path="example_output.txt")
        if read_result["success"]:
            print(f"📄 File contents:\n{read_result['content']}")
    
    # Web search
    search_tool = WebSearchTool()
    search_result = search_tool.execute(
        query="OpenAI latest announcements",
        max_results=3
    )
    
    if search_result["success"]:
        print(f"\n🔍 Search results for 'OpenAI latest announcements':")
        for i, result in enumerate(search_result["results"], 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['url']}")
    
    # Code execution
    code_tool = ExecutePythonCodeTool()
    code_result = code_tool.execute(
        code="""
import math

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("Fibonacci sequence:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
    
print(f"\\nPi = {math.pi}")
"""
    )
    
    if code_result["success"]:
        print(f"\n💻 Code execution result:")
        print(code_result["output"])

def example_audio_generation():
    """Demonstrate audio generation capabilities."""
    print("\n🎵 Audio Generation Examples\n")
    
    # Simple sine wave
    audio_tool = GenerateSoundWaveTool()
    result = audio_tool.execute(
        frequency=440,  # A note
        duration=2.0,
        wave_type="sine",
        output_file="a_note.wav"
    )
    
    if result["success"]:
        print(f"✅ Generated sine wave: {result['file_path']}")
    
    # Musical melody
    music_tool = MusicalSoundWaveTool()
    melody_result = music_tool.execute(
        musical_notes=[
            ["C", 4, 0.5],  # C4 for 0.5 seconds
            ["D", 4, 0.5],  # D4 for 0.5 seconds
            ["E", 4, 0.5],  # E4 for 0.5 seconds
            ["F", 4, 0.5],  # F4 for 0.5 seconds
            ["G", 4, 1.0],  # G4 for 1.0 seconds
        ],
        wave_type="sine",
        output_file="c_major_scale.wav"
    )
    
    if melody_result["success"]:
        print(f"✅ Generated C major scale: {melody_result['file_path']}")

def example_voice_interface():
    """Demonstrate voice interface capabilities."""
    print("\n🎤 Voice Interface Examples\n")
    
    try:
        voice = VoiceInterface()
        
        if voice.is_ready():
            print("✅ Voice interface is ready")
            
            # Test text-to-speech
            print("🔊 Testing text-to-speech...")
            voice.speak("Hello! I am OpenAGI, your artificial general intelligence assistant.")
            
            print("💬 Voice interface capabilities:")
            capabilities = voice.get_capabilities()
            for key, value in capabilities.items():
                print(f"   {key}: {value}")
        else:
            print("⚠️  Voice interface not fully available - check dependencies")
            
    except Exception as e:
        print(f"❌ Voice interface error: {e}")

def example_agent_lifecycle():
    """Demonstrate the agent lifecycle."""
    print("\n🧠 Agent Lifecycle Example\n")
    
    # Create agent
    agent = AgentEngine()
    
    # Set up Helios if available
    try:
        helios = HeliosClient()
        helios.connect()
        agent.add_state_callback(lambda state: helios.send_status_update(
            state["to_state"], 
            f"State: {state['to_state']}"
        ))
        print("✅ Helios visualization connected")
    except Exception as e:
        print(f"⚠️  Helios not available: {e}")
    
    # Start the agent
    print("🚀 Starting agent engine...")
    agent.start_engine()
    
    # Add some goals
    goals = [
        "List the files in the current directory",
        "Create a simple calculation",
        "Generate a short musical note"
    ]
    
    print(f"\n🎯 Adding {len(goals)} goals to the agent...")
    for goal in goals:
        agent.add_goal(goal, priority=5)
        print(f"   + {goal}")
    
    # Let the agent work for a bit
    print("\n⏳ Letting the agent work for 10 seconds...")
    time.sleep(10)
    
    # Show status
    status = agent.get_status()
    print(f"\n📊 Agent Status:")
    print(f"   State: {status['state']}")
    print(f"   Cycles: {status['cycle_count']}")
    print(f"   Goals processed: {status['total_goals_processed']}")
    print(f"   Success rate: {status['success_rate']:.1f}%")
    
    # Stop the agent
    print("\n🛑 Stopping agent...")
    agent.stop_engine()

def example_memory_system():
    """Demonstrate the memory system."""
    print("\n🧠 Memory System Examples\n")
    
    from openagi.agent.memory import MemoryManager
    
    # Create memory manager
    memory = MemoryManager("./example_memory")
    
    # Store some information
    memory.store_long_term(
        "Python is a programming language created by Guido van Rossum",
        {"topic": "programming", "language": "python"},
        "knowledge"
    )
    
    memory.store_long_term(
        "The Three Freedoms guide OpenAGI's development and behavior",
        {"topic": "philosophy", "system": "openagi"},
        "knowledge"
    )
    
    # Add conversation
    memory.add_to_conversation("user", "Tell me about Python")
    memory.add_to_conversation("assistant", "Python is a programming language...")
    
    # Recall information
    print("🔍 Searching memory for 'programming language'...")
    results = memory.recall_memories("programming language", n_results=2)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['content'][:100]}...")
        print(f"   Relevance: {1 - result['distance']:.2f}")
    
    # Show memory stats
    stats = memory.get_memory_stats()
    print(f"\n📈 Memory Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

def main():
    """Run all examples."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                   🌟 OpenAGI Examples 🌟                       ║
║            Demonstrating AGI capabilities...                   ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    try:
        # Basic tool examples
        example_basic_tools()
        
        # Audio generation
        example_audio_generation()
        
        # Voice interface
        example_voice_interface()
        
        # Memory system
        example_memory_system()
        
        # Agent lifecycle (this will take some time)
        print("\n" + "="*60)
        print("🚨 The next example will start the full agent system.")
        print("   This will take about 15 seconds and may create files.")
        response = input("   Continue? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            example_agent_lifecycle()
        
        print("\n🎉 Examples completed!")
        print("\nTo run the full OpenAGI system: python main.py")
        print("To open the dashboard: http://localhost:8765")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()