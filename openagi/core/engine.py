"""Core engine for OpenAGI platform."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json

from ..config.settings import Config
from ..learning.self_learning import SelfLearningSystem
from ..plugins.manager import PluginManager
from .agent import AIAgent


class OpenAGIEngine:
    """
    Core engine that orchestrates the OpenAGI platform.
    
    Manages agents, learning systems, plugins, and coordinates
    all AI operations with self-learning capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.logger = self._setup_logging()
        
        # Core components
        self.learning_system = SelfLearningSystem(self.config)
        self.plugin_manager = PluginManager(self.config)
        self.agents: Dict[str, AIAgent] = {}
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "learning_iterations": 0,
            "plugins_loaded": 0,
            "agents_created": 0,
            "start_time": datetime.now(),
        }
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        self.logger.info("OpenAGI Engine initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("openagi")
        logger.setLevel(self.config.get("logging.level", "INFO"))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> None:
        """Initialize all engine components."""
        self.logger.info("Initializing OpenAGI Engine components...")
        
        # Initialize learning system
        await self.learning_system.initialize()
        
        # Load plugins
        await self.plugin_manager.load_plugins()
        self.metrics["plugins_loaded"] = len(self.plugin_manager.plugins)
        
        # Initialize default agents
        await self._create_default_agents()
        
        self.logger.info(f"Engine initialized with {self.metrics['plugins_loaded']} plugins")
    
    async def _create_default_agents(self) -> None:
        """Create default AI agents."""
        default_agents = self.config.get("agents.default", [])
        
        for agent_config in default_agents:
            agent = AIAgent(
                name=agent_config["name"],
                capabilities=agent_config.get("capabilities", []),
                config=agent_config
            )
            await self.register_agent(agent)
    
    async def register_agent(self, agent: AIAgent) -> None:
        """Register a new AI agent."""
        self.agents[agent.name] = agent
        await agent.initialize(self.learning_system)
        self.metrics["agents_created"] += 1
        
        self.logger.info(f"Agent '{agent.name}' registered")
        await self._emit_event("agent_registered", {"agent": agent.name})
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task using appropriate agents."""
        task_id = task.get("id", f"task_{datetime.now().timestamp()}")
        self.logger.info(f"Processing task: {task_id}")
        
        try:
            # Select best agent for task
            agent = await self._select_agent(task)
            
            # Process task
            result = await agent.process_task(task)
            
            # Learn from the task
            await self.learning_system.learn_from_task(task, result)
            
            # Update metrics
            self.metrics["tasks_completed"] += 1
            
            await self._emit_event("task_completed", {
                "task_id": task_id,
                "agent": agent.name,
                "result": result
            })
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "agent": agent.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {str(e)}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _select_agent(self, task: Dict[str, Any]) -> AIAgent:
        """Select the best agent for a given task."""
        task_type = task.get("type", "general")
        required_capabilities = task.get("capabilities", [])
        
        # Find agents with matching capabilities
        suitable_agents = []
        for agent in self.agents.values():
            if agent.can_handle_task(task_type, required_capabilities):
                suitable_agents.append(agent)
        
        if not suitable_agents:
            # Create a general-purpose agent if none available
            agent = AIAgent(
                name=f"auto_agent_{len(self.agents)}",
                capabilities=["general"],
                config={"auto_created": True}
            )
            await self.register_agent(agent)
            return agent
        
        # Select best agent based on performance history
        return max(suitable_agents, key=lambda a: a.performance_score)
    
    async def evolve(self) -> None:
        """Trigger evolution/learning cycle."""
        self.logger.info("Starting evolution cycle...")
        
        # Update learning system
        await self.learning_system.evolve()
        
        # Update agents
        for agent in self.agents.values():
            await agent.evolve()
        
        self.metrics["learning_iterations"] += 1
        await self._emit_event("evolution_completed", {
            "iteration": self.metrics["learning_iterations"]
        })
    
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register an event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def _emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    await handler(event, data)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        uptime = datetime.now() - self.metrics["start_time"]
        
        return {
            "status": "running",
            "uptime_seconds": uptime.total_seconds(),
            "metrics": self.metrics.copy(),
            "agents": list(self.agents.keys()),
            "plugins": list(self.plugin_manager.plugins.keys()),
            "learning_status": self.learning_system.get_status()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the engine."""
        self.logger.info("Shutting down OpenAGI Engine...")
        
        # Save learning state
        await self.learning_system.save_state()
        
        # Cleanup agents
        for agent in self.agents.values():
            await agent.cleanup()
        
        self.logger.info("OpenAGI Engine shutdown complete")