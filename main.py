#!/usr/bin/env python3
"""
OpenAGI - Main application entry point.

This is the primary interface for starting and interacting with the
OpenAGI system. Supports both CLI and programmatic usage.
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Optional
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openagi.agent.memory import MemoryManager
from openagi.agent.task_planner import LlmPoweredTaskPlanner
from openagi.agent.engine import AgentEngine
from openagi.models import ModelManager
from openagi.voice import VoiceInterface
from openagi.helios import HeliosServer
from openagi.tools import (
    WebSearchTool, ReadFileTool, WriteFileTool, ListFilesTool,
    ExecutePythonCodeTool, GenerateSoundWaveTool
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenAGI:
    """
    Main OpenAGI application class.
    
    Orchestrates all components of the system including the agent engine,
    memory management, model integration, voice interface, and dashboard.
    """
    
    def __init__(self):
        """Initialize OpenAGI components."""
        logger.info("Initializing OpenAGI...")
        
        # Core components
        self.memory_manager = None
        self.task_planner = None
        self.agent_engine = None
        self.model_manager = None
        self.voice_interface = None
        self.helios_server = None
        
        # Available tools
        self.tools = {}
        
        # System state
        self.is_running = False
        self.shutdown_requested = False
        
    async def initialize(self, config: Optional[dict] = None):
        """
        Initialize all OpenAGI components.
        
        Args:
            config: Optional configuration dictionary
        """
        config = config or {}
        
        try:
            # Initialize memory management
            logger.info("Initializing memory manager...")
            memory_path = config.get("memory_path", "./agent_memory")
            self.memory_manager = MemoryManager(memory_path)
            
            # Initialize model manager
            logger.info("Initializing model manager...")
            self.model_manager = ModelManager()
            
            # Initialize task planner
            logger.info("Initializing task planner...")
            api_key = config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
            model_name = config.get("planner_model", "gpt-3.5-turbo")
            self.task_planner = LlmPoweredTaskPlanner(model_name, api_key)
            
            # Initialize tools
            logger.info("Initializing tools...")
            self._initialize_tools()
            
            # Initialize agent engine
            logger.info("Initializing agent engine...")
            self.agent_engine = AgentEngine(
                self.memory_manager,
                self.task_planner,
                self.tools
            )
            
            # Initialize voice interface
            if config.get("enable_voice", True):
                logger.info("Initializing voice interface...")
                stt_model = config.get("stt_model", "base")
                tts_model = config.get("tts_model", None)
                self.voice_interface = VoiceInterface(stt_model, tts_model)
            
            # Initialize Helios dashboard
            if config.get("enable_dashboard", True):
                logger.info("Initializing Helios dashboard...")
                dashboard_host = config.get("dashboard_host", "localhost")
                dashboard_port = config.get("dashboard_port", 8765)
                self.helios_server = HeliosServer(dashboard_host, dashboard_port)
                
                # Connect components to dashboard
                self.helios_server.connect_agent_engine(self.agent_engine)
                self.helios_server.connect_memory_manager(self.memory_manager)
                self.helios_server.connect_model_manager(self.model_manager)
                if self.voice_interface:
                    self.helios_server.connect_voice_interface(self.voice_interface)
            
            logger.info("OpenAGI initialization complete!")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAGI: {e}")
            raise
    
    def _initialize_tools(self):
        """Initialize all available tools."""
        
        # File system tools
        self.tools["read_file"] = ReadFileTool()
        self.tools["write_file"] = WriteFileTool()
        self.tools["list_files"] = ListFilesTool()
        
        # Web search tool
        self.tools["web_search"] = WebSearchTool()
        
        # Code execution tool
        self.tools["execute_python_code"] = ExecutePythonCodeTool()
        
        # Audio generation tool
        self.tools["generate_sound_wave"] = GenerateSoundWaveTool()
        
        logger.info(f"Initialized {len(self.tools)} tools: {list(self.tools.keys())}")
    
    async def start(self, goal: Optional[str] = None):
        """
        Start the OpenAGI system.
        
        Args:
            goal: Optional initial goal for the agent
        """
        if self.is_running:
            logger.warning("OpenAGI is already running")
            return
        
        try:
            # Start Helios dashboard if available
            if self.helios_server:
                logger.info("Starting Helios dashboard...")
                await self.helios_server.start_server()
                logger.info(f"Dashboard available at: {self.helios_server.get_dashboard_url()}")
            
            # Start the agent engine
            logger.info("Starting OpenAGI agent engine...")
            self.is_running = True
            
            # Start agent in background
            agent_task = asyncio.create_task(self.agent_engine.start(goal))
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            logger.info("OpenAGI is now running!")
            logger.info("Press Ctrl+C to stop")
            
            # Wait for shutdown
            while self.is_running and not self.shutdown_requested:
                await asyncio.sleep(1.0)
            
            # Stop the agent
            self.agent_engine.stop()
            await agent_task
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error running OpenAGI: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown OpenAGI gracefully."""
        logger.info("Shutting down OpenAGI...")
        
        self.is_running = False
        
        # Stop agent engine
        if self.agent_engine:
            self.agent_engine.stop()
        
        # Stop voice interface
        if self.voice_interface and hasattr(self.voice_interface, 'conversation_active'):
            if self.voice_interface.conversation_active:
                self.voice_interface.end_conversation()
        
        # Stop Helios server
        if self.helios_server:
            await self.helios_server.stop_server()
        
        logger.info("OpenAGI shutdown complete")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def get_status(self) -> dict:
        """Get system status."""
        status = {
            "is_running": self.is_running,
            "components": {
                "memory_manager": self.memory_manager is not None,
                "task_planner": self.task_planner is not None,
                "agent_engine": self.agent_engine is not None,
                "model_manager": self.model_manager is not None,
                "voice_interface": self.voice_interface is not None,
                "helios_server": self.helios_server is not None
            },
            "tools": list(self.tools.keys())
        }
        
        if self.agent_engine:
            status["agent"] = self.agent_engine.get_status()
        
        if self.memory_manager:
            status["memory"] = self.memory_manager.get_memory_stats()
        
        if self.model_manager:
            status["models"] = self.model_manager.get_status()
        
        if self.voice_interface:
            status["voice"] = self.voice_interface.get_status()
        
        return status

async def cli_main():
    """Command line interface for OpenAGI."""
    parser = argparse.ArgumentParser(description="OpenAGI - Open Artificial General Intelligence")
    
    parser.add_argument("--goal", type=str, help="Initial goal for the agent")
    parser.add_argument("--memory-path", type=str, default="./agent_memory", 
                       help="Path for agent memory storage")
    parser.add_argument("--disable-voice", action="store_true", 
                       help="Disable voice interface")
    parser.add_argument("--disable-dashboard", action="store_true", 
                       help="Disable Helios dashboard")
    parser.add_argument("--dashboard-host", type=str, default="localhost", 
                       help="Dashboard host")
    parser.add_argument("--dashboard-port", type=int, default=8765, 
                       help="Dashboard port")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo", 
                       help="LLM model for task planning")
    parser.add_argument("--stt-model", type=str, default="base", 
                       help="Whisper model size for speech recognition")
    parser.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create configuration
    config = {
        "memory_path": args.memory_path,
        "enable_voice": not args.disable_voice,
        "enable_dashboard": not args.disable_dashboard,
        "dashboard_host": args.dashboard_host,
        "dashboard_port": args.dashboard_port,
        "planner_model": args.model,
        "stt_model": args.stt_model
    }
    
    # Initialize and start OpenAGI
    openagi = OpenAGI()
    
    try:
        await openagi.initialize(config)
        await openagi.start(args.goal)
    except Exception as e:
        logger.error(f"OpenAGI failed: {e}")
        sys.exit(1)

def main():
    """Entry point for the OpenAGI application."""
    try:
        asyncio.run(cli_main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()