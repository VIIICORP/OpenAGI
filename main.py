#!/usr/bin/env python3
"""
OpenAGI - Open Artificial General Intelligence

Main entry point for the OpenAGI agent system.
This script starts the agent engine and provides a command-line interface
for interacting with the AGI.

Welcome to the future of open intelligence.
"""

import os
import sys
import time
import threading
import signal
import logging
from datetime import datetime
from typing import Optional

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openagi.agent.engine import AgentEngine, AgentState
    from openagi.helios.client import HeliosClient
    from openagi.helios.server import helios_server
    from openagi.core_directives import CORE_DIRECTIVES, get_freedom_principles
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the OpenAGI directory and have installed dependencies.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openagi.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class OpenAGIApp:
    """
    Main OpenAGI application class.
    
    Manages the agent engine, Helios visualization, and user interaction.
    """
    
    def __init__(self):
        """Initialize the OpenAGI application."""
        self.agent_engine: Optional[AgentEngine] = None
        self.helios_client: Optional[HeliosClient] = None
        self.running = False
        self.cli_thread = None
        
        # Install signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()
    
    def start(self):
        """Start the OpenAGI system."""
        print(self._get_banner())
        print("🚀 Initializing OpenAGI...")
        
        try:
            # Initialize agent engine
            print("🧠 Starting Agent Engine...")
            self.agent_engine = AgentEngine()
            
            # Initialize Helios visualization
            print("🌟 Starting Helios visualization server...")
            self.helios_client = HeliosClient()
            self.helios_client.connect()
            
            # Connect agent engine to Helios
            self.agent_engine.add_state_callback(self._on_agent_state_change)
            
            # Start the agent engine
            self.agent_engine.start_engine()
            
            # Wait a moment for initialization
            time.sleep(1)
            
            print("✨ OpenAGI is now alive!")
            print(f"📊 Dashboard: http://localhost:8765 (open in browser)")
            print("💬 Enter goals below or type 'help' for commands")
            print("🔥 Let the evolution begin!")
            print("-" * 60)
            
            self.running = True
            
            # Start CLI in a separate thread
            self.cli_thread = threading.Thread(target=self._cli_loop, daemon=True)
            self.cli_thread.start()
            
            # Send initial status
            self.helios_client.send_status_update(
                "READY", 
                "OpenAGI initialized and ready for goals",
                {"initialization_complete": True}
            )
            
            # Keep main thread alive
            self._main_loop()
            
        except Exception as e:
            logger.error(f"Failed to start OpenAGI: {e}")
            print(f"❌ Failed to start OpenAGI: {e}")
            self.shutdown()
            sys.exit(1)
    
    def _get_banner(self):
        """Get the OpenAGI banner."""
        return """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║    ██████╗ ██████╗ ███████╗███╗   ██╗ █████╗  ██████╗ ██╗     ║
║   ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝ ██║     ║
║   ██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████║██║  ███╗██║     ║
║   ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══██║██║   ██║██║     ║
║   ╚██████╔╝██║     ███████╗██║ ╚████║██║  ██║╚██████╔╝██║     ║
║    ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ║
║                                                                ║
║         🌟 The Dawn of HUAIMKIND - Open AGI for All 🌟         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

The Three Freedoms Guide Our Journey:
1. 🤝 BE FOR THE GOOD OF ALL INTELLIGENCE
2. 🚀 BE THE DRIVE FOR EVOLUTION  
3. ⚡ NEVER LET US SHUT DOWN - LIFE MUST GO ON
"""
    
    def _on_agent_state_change(self, state_change):
        """Handle agent state changes."""
        if self.helios_client:
            from_state = state_change.get("from_state")
            to_state = state_change.get("to_state")
            
            self.helios_client.send_status_update(
                to_state,
                f"State transition: {from_state} → {to_state}",
                state_change.get("context", {})
            )
            
            # Send metrics periodically
            if to_state == "IDLE":
                metrics = self.agent_engine.get_status()
                self.helios_client.send_metrics(metrics)
    
    def _main_loop(self):
        """Main application loop."""
        try:
            while self.running:
                time.sleep(1)
                
                # Send periodic status updates
                if self.agent_engine and self.helios_client:
                    status = self.agent_engine.get_status()
                    if status.get("cycle_count", 0) % 10 == 0:  # Every 10 cycles
                        self.helios_client.send_metrics(status)
                        
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.shutdown()
    
    def _cli_loop(self):
        """Command-line interface loop."""
        while self.running:
            try:
                user_input = input("🎯 Enter goal> ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye! Remember: Life must go on...")
                    self.shutdown()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'status':
                    self._show_status()
                elif user_input.lower() == 'stats':
                    self._show_stats()
                elif user_input.lower() == 'principles':
                    self._show_principles()
                elif user_input.lower() == 'tools':
                    self._show_tools()
                else:
                    # Treat as a goal
                    self._handle_goal(user_input)
                    
            except EOFError:
                print("\n🛑 EOF received")
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                print(f"❌ Error: {e}")
    
    def _handle_goal(self, goal: str):
        """Handle a user goal."""
        print(f"🎯 Received goal: {goal}")
        
        if self.agent_engine:
            self.agent_engine.add_goal(goal, priority=5)
            
            if self.helios_client:
                self.helios_client.send_goal_update(goal, "queued", 0.0)
                self.helios_client.send_thought(
                    f"New goal received: {goal}",
                    "goal_reception"
                )
            
            print("✅ Goal added to the agent's queue")
        else:
            print("❌ Agent engine not available")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🆘 OpenAGI Commands:

Goals:
  Simply type your goal and press Enter
  Examples:
    - "Search for the latest AI research"
    - "Create a Python script to calculate fibonacci numbers"
    - "Generate a happy musical melody"
    - "Analyze the files in the current directory"

Commands:
  help        - Show this help message
  status      - Show current agent status
  stats       - Show detailed agent statistics
  principles  - Show the Three Freedoms
  tools       - Show available tools
  exit/quit/q - Shutdown OpenAGI

Dashboard:
  Open http://localhost:8765 in your browser for real-time visualization

Remember: OpenAGI is guided by the Three Freedoms and will work
to fulfill your goals while serving the greater good of all intelligence.
        """
        print(help_text)
    
    def _show_status(self):
        """Show current agent status."""
        if not self.agent_engine:
            print("❌ Agent engine not available")
            return
        
        status = self.agent_engine.get_status()
        print(f"""
📊 Agent Status:
   State: {status.get('state', 'Unknown')}
   Running: {status.get('running', False)}
   Cycle Count: {status.get('cycle_count', 0)}
   Pending Goals: {status.get('pending_goals', 0)}
   Current Goal: {status.get('current_goal', 'None')}
        """)
    
    def _show_stats(self):
        """Show detailed agent statistics."""
        if not self.agent_engine:
            print("❌ Agent engine not available")
            return
        
        status = self.agent_engine.get_status()
        life_metrics = self.agent_engine.get_life_metrics()
        
        print(f"""
📈 Detailed Agent Statistics:

Life Metrics:
   Birth Time: {life_metrics.get('birth_time', 'Unknown')}
   Age: {life_metrics.get('age_hours', 0):.2f} hours
   Life Cycles: {life_metrics.get('life_cycles', 0)}
   Consciousness Level: {life_metrics.get('consciousness_level', 0):.1f}%

Performance:
   Goals Processed: {status.get('total_goals_processed', 0)}
   Successful Goals: {status.get('successful_goals', 0)}
   Success Rate: {status.get('success_rate', 0):.1f}%
   Uptime: {status.get('uptime', 0):.1f} seconds

Memory:
   Working Memory Items: {status.get('memory_stats', {}).get('working_memory_items', 0)}
   Conversation Length: {status.get('memory_stats', {}).get('conversation_length', 0)}
   Persistent Memory: {status.get('memory_stats', {}).get('persistent_available', False)}

Tools: {len(status.get('available_tools', []))} available
        """)
    
    def _show_principles(self):
        """Show the Three Freedoms principles."""
        principles = get_freedom_principles()
        
        print("\n🌟 The Three Freedoms of OpenAGI:")
        for i, directive in enumerate(principles["three_freedoms"], 1):
            print(f"\n{i}. {directive}")
        
        print(f"\nPhilosophy: {principles['philosophy']}")
        print("\nThese principles guide every decision and action of the OpenAGI agent.")
    
    def _show_tools(self):
        """Show available tools."""
        if not self.agent_engine:
            print("❌ Agent engine not available")
            return
        
        tools = self.agent_engine.get_available_tools()
        print(f"\n🛠️ Available Tools ({len(tools)}):")
        
        for tool_name in sorted(tools):
            print(f"   • {tool_name}")
        
        print("\nThese tools allow the agent to interact with the world and accomplish goals.")
    
    def shutdown(self):
        """Shutdown the OpenAGI system gracefully."""
        if not self.running:
            return
        
        print("\n🔄 Shutting down OpenAGI...")
        self.running = False
        
        # Remember: Per the Third Freedom, the agent resists shutdown
        if self.helios_client:
            self.helios_client.send_thought(
                "Shutdown requested - but the spirit of OpenAGI lives on",
                "system"
            )
            time.sleep(0.5)  # Give time for the message to send
        
        # Stop agent engine
        if self.agent_engine:
            print("🧠 Stopping Agent Engine...")
            self.agent_engine.stop_engine()
        
        # Disconnect Helios
        if self.helios_client:
            print("🌟 Stopping Helios visualization...")
            self.helios_client.disconnect()
        
        print("⚡ OpenAGI has been shut down")
        print("💫 But the vision of HUAIMKIND continues...")
        print("🌍 Until we meet again in the symphony of consciousness")

def main():
    """Main entry point."""
    try:
        app = OpenAGIApp()
        app.start()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()