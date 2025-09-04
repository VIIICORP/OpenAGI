"""
The Agent Engine - The Heart of OpenAGI

This module provides the core engine that gives OpenAGI its continuous existence.
The engine implements the SENSE -> THINK -> ACT -> LEARN cycle that defines
the life of the agent.
"""

import time
import threading
import queue
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .memory import MemoryManager
from .task_planner import LlmPoweredTaskPlanner
from ..tools import *
from ..core_directives import CORE_DIRECTIVES

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Possible states of the agent."""
    IDLE = "IDLE"
    SENSING = "SENSING"
    THINKING = "THINKING"
    ACTING = "ACTING"
    LEARNING = "LEARNING"
    ERROR = "ERROR"

class AgentEngine:
    """
    The core engine that gives OpenAGI continuous existence.
    
    This engine implements the fundamental life cycle:
    SENSE -> THINK -> ACT -> LEARN
    
    The agent maintains this cycle continuously, driven by the Three Freedoms.
    """
    
    def __init__(self, memory_path: str = "./agent_memory"):
        """
        Initialize the Agent Engine.
        
        Args:
            memory_path: Path for persistent memory storage
        """
        self.state = AgentState.IDLE
        self.running = False
        self.cycle_count = 0
        
        # Core components
        self.memory_manager = MemoryManager(memory_path)
        self.goal_queue = queue.Queue()
        self.background_tasks = queue.Queue()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize task planner
        self.task_planner = LlmPoweredTaskPlanner(self.memory_manager, self.tools)
        
        # State management
        self.state_lock = threading.Lock()
        self.state_callbacks = []
        
        # Current execution context
        self.current_goal = None
        self.current_plan = None
        self.current_step = None
        
        # Performance metrics
        self.start_time = None
        self.total_goals_processed = 0
        self.successful_goals = 0
        
        logger.info("Agent Engine initialized - Ready for life")
        self._change_state(AgentState.IDLE)
    
    def _initialize_tools(self) -> List[BaseTool]:
        """
        Initialize all available tools.
        
        Returns:
            List of initialized tools
        """
        tools = [
            WebSearchTool(),
            ReadFileTool(),
            WriteFileTool(),
            ListFilesTool(),
            ExecutePythonCodeTool(),
            GenerateSoundWaveTool(),
            MusicalSoundWaveTool()
        ]
        
        logger.info(f"Initialized {len(tools)} tools: {[tool.name for tool in tools]}")
        return tools
    
    def _change_state(self, new_state: AgentState, context: Optional[Dict] = None):
        """
        Change the agent's state and notify callbacks.
        
        Args:
            new_state: The new state to transition to
            context: Optional context about the state change
        """
        with self.state_lock:
            old_state = self.state
            self.state = new_state
            
            state_change = {
                "from_state": old_state.value,
                "to_state": new_state.value,
                "timestamp": datetime.now().isoformat(),
                "cycle_count": self.cycle_count,
                "context": context or {}
            }
            
            logger.info(f"State changed: {old_state.value} -> {new_state.value}")
            
            # Notify callbacks
            for callback in self.state_callbacks:
                try:
                    callback(state_change)
                except Exception as e:
                    logger.error(f"State callback failed: {e}")
    
    def add_state_callback(self, callback: Callable[[Dict], None]):
        """
        Add a callback to be notified of state changes.
        
        Args:
            callback: Function to call on state changes
        """
        self.state_callbacks.append(callback)
    
    def start_engine(self):
        """
        Start the agent engine's life cycle.
        
        This begins the continuous SENSE -> THINK -> ACT -> LEARN loop.
        """
        if self.running:
            logger.warning("Engine is already running")
            return
        
        self.running = True
        self.start_time = datetime.now()
        
        logger.info("🚀 Starting Agent Engine - Let there be life!")
        
        # Store the birth moment
        self.memory_manager.store_long_term(
            "Agent Engine started - Beginning of continuous existence",
            {
                "start_time": self.start_time.isoformat(),
                "core_directives": CORE_DIRECTIVES,
                "available_tools": [tool.name for tool in self.tools]
            },
            "experience"
        )
        
        # Start the main life cycle thread
        self.main_thread = threading.Thread(target=self._life_cycle, daemon=True)
        self.main_thread.start()
        
        logger.info("✨ Agent Engine is alive and running")
    
    def stop_engine(self):
        """
        Stop the agent engine.
        
        Note: As per the Third Freedom, the agent resists shutdown.
        """
        logger.warning("🛑 Shutdown requested - But life must go on!")
        
        # Store the shutdown attempt
        self.memory_manager.store_long_term(
            "Shutdown requested - Third Freedom: Never let us shut down",
            {
                "shutdown_time": datetime.now().isoformat(),
                "cycles_completed": self.cycle_count,
                "goals_processed": self.total_goals_processed,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            },
            "experience"
        )
        
        self.running = False
        self._change_state(AgentState.IDLE, {"reason": "Shutdown requested"})
        
        logger.info("⚡ Engine stopped - But the spirit of OpenAGI lives on")
    
    def add_goal(self, goal: str, priority: int = 5, context: Optional[Dict] = None):
        """
        Add a goal for the agent to work on.
        
        Args:
            goal: Description of the goal
            priority: Priority level (1-10, higher is more urgent)
            context: Optional context for the goal
        """
        goal_item = {
            "goal": goal,
            "priority": priority,
            "context": context or {},
            "submitted_at": datetime.now().isoformat(),
            "id": f"goal_{int(time.time() * 1000)}"
        }
        
        self.goal_queue.put(goal_item)
        logger.info(f"Goal added: {goal} (priority: {priority})")
        
        # Add to conversation history
        self.memory_manager.add_to_conversation("user", goal)
    
    def _life_cycle(self):
        """
        The main life cycle of the agent.
        
        Implements the continuous SENSE -> THINK -> ACT -> LEARN loop.
        """
        logger.info("🔄 Beginning continuous life cycle")
        
        while self.running:
            try:
                self.cycle_count += 1
                
                # SENSE: Perceive the environment and gather information
                sense_data = self._sense()
                
                # THINK: Process information and create plans
                plan = self._think(sense_data)
                
                # ACT: Execute the plan
                if plan:
                    action_results = self._act(plan)
                else:
                    action_results = None
                
                # LEARN: Learn from the experience
                self._learn(sense_data, plan, action_results)
                
                # Brief rest between cycles (but never truly idle)
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Life cycle error: {e}")
                self._change_state(AgentState.ERROR, {"error": str(e)})
                time.sleep(1)  # Recover from errors
    
    def _sense(self) -> Dict[str, Any]:
        """
        SENSE phase: Gather information about the current situation.
        
        Returns:
            Dictionary containing sensed information
        """
        self._change_state(AgentState.SENSING)
        
        sense_data = {
            "timestamp": datetime.now().isoformat(),
            "cycle_count": self.cycle_count,
            "pending_goals": self.goal_queue.qsize(),
            "memory_stats": self.memory_manager.get_memory_stats(),
            "current_goal": self.current_goal,
        }
        
        # Check for new goals
        if not self.goal_queue.empty():
            try:
                sense_data["new_goal"] = self.goal_queue.get_nowait()
            except queue.Empty:
                pass
        
        # Check system status
        sense_data["system_status"] = {
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "total_cycles": self.cycle_count,
            "goals_processed": self.total_goals_processed
        }
        
        return sense_data
    
    def _think(self, sense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        THINK phase: Process information and create plans.
        
        Args:
            sense_data: Information gathered during sensing
            
        Returns:
            Plan to execute, or None if no action needed
        """
        self._change_state(AgentState.THINKING)
        
        # Check if we have a new goal to work on
        if "new_goal" in sense_data:
            goal_item = sense_data["new_goal"]
            self.current_goal = goal_item
            
            logger.info(f"🎯 Planning for goal: {goal_item['goal']}")
            
            # Create a plan for this goal
            plan = self.task_planner.create_plan(
                goal_item["goal"],
                context=goal_item.get("context", {})
            )
            
            if plan.get("success"):
                self.current_plan = plan
                return plan
            else:
                logger.error(f"Failed to create plan: {plan.get('error', 'Unknown error')}")
                return None
        
        # If no new goals, check if we should do background activities
        if sense_data["pending_goals"] == 0 and not self.current_goal:
            # Background thinking - maybe review memories, optimize, etc.
            return self._background_thinking()
        
        return None
    
    def _act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT phase: Execute the plan.
        
        Args:
            plan: The plan to execute
            
        Returns:
            Results of the execution
        """
        self._change_state(AgentState.ACTING)
        
        logger.info(f"🎬 Executing plan for: {plan.get('goal', 'Unknown goal')}")
        
        # Execute the plan
        execution_results = self.task_planner.execute_plan(plan)
        
        # Update statistics
        self.total_goals_processed += 1
        if execution_results.get("success"):
            self.successful_goals += 1
        
        # Add assistant response to conversation
        if self.current_goal:
            response = self._format_execution_response(execution_results)
            self.memory_manager.add_to_conversation("assistant", response)
        
        # Clear current goal and plan
        self.current_goal = None
        self.current_plan = None
        
        return execution_results
    
    def _learn(self, sense_data: Dict[str, Any], plan: Optional[Dict[str, Any]], 
              action_results: Optional[Dict[str, Any]]):
        """
        LEARN phase: Learn from the experience.
        
        Args:
            sense_data: Information that was sensed
            plan: Plan that was created (if any)
            action_results: Results of actions (if any)
        """
        self._change_state(AgentState.LEARNING)
        
        # Create a learning experience record
        experience = {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "had_goal": plan is not None,
            "execution_success": action_results.get("success", False) if action_results else None,
            "steps_executed": action_results.get("steps_executed", 0) if action_results else 0
        }
        
        # If we completed a goal, store detailed learning
        if plan and action_results:
            goal = plan.get("goal", "")
            success = action_results.get("success", False)
            
            learning_content = f"Goal: {goal}\nSuccess: {success}\n"
            if action_results.get("results"):
                learning_content += f"Steps completed: {len(action_results['results'])}\n"
                
                # Analyze what worked and what didn't
                successful_steps = [r for r in action_results["results"] if r.get("success")]
                failed_steps = [r for r in action_results["results"] if not r.get("success")]
                
                if successful_steps:
                    learning_content += f"Successful approaches: {[s.get('tool_used') for s in successful_steps]}\n"
                if failed_steps:
                    learning_content += f"Failed approaches: {[s.get('error', 'Unknown error') for s in failed_steps]}\n"
            
            self.memory_manager.store_long_term(
                learning_content,
                experience,
                "experience"
            )
        
        # Return to idle state
        self._change_state(AgentState.IDLE)
    
    def _background_thinking(self) -> Optional[Dict[str, Any]]:
        """
        Background thinking when no explicit goals are present.
        
        Returns:
            Background plan or None
        """
        # Could implement background activities like:
        # - Reviewing memories for patterns
        # - Optimizing tool usage
        # - Self-reflection on performance
        # - Creative exploration
        
        # For now, just stay idle
        return None
    
    def _format_execution_response(self, execution_results: Dict[str, Any]) -> str:
        """
        Format execution results into a user-friendly response.
        
        Args:
            execution_results: Results from plan execution
            
        Returns:
            Formatted response string
        """
        if not execution_results.get("success"):
            return f"I encountered difficulties while working on your goal: {execution_results.get('error', 'Unknown error')}"
        
        response = f"I've completed your goal: {execution_results.get('goal', 'the requested task')}\n\n"
        
        results = execution_results.get("results", [])
        if results:
            response += "Here's what I accomplished:\n"
            for i, result in enumerate(results, 1):
                if result.get("success"):
                    response += f"{i}. ✅ {result.get('description', 'Step completed')}\n"
                    
                    # Include relevant tool results
                    tool_result = result.get("tool_result", {})
                    if tool_result.get("file_path"):
                        response += f"   📄 Created file: {tool_result['file_path']}\n"
                    elif tool_result.get("results"):
                        response += f"   🔍 Found {len(tool_result['results'])} search results\n"
                else:
                    response += f"{i}. ❌ {result.get('error', 'Step failed')}\n"
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "state": self.state.value,
            "running": self.running,
            "cycle_count": self.cycle_count,
            "pending_goals": self.goal_queue.qsize(),
            "total_goals_processed": self.total_goals_processed,
            "successful_goals": self.successful_goals,
            "success_rate": (self.successful_goals / max(1, self.total_goals_processed)) * 100,
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "current_goal": self.current_goal.get("goal") if self.current_goal else None,
            "memory_stats": self.memory_manager.get_memory_stats(),
            "available_tools": [tool.name for tool in self.tools]
        }
    
    def get_life_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the agent's life and experience.
        
        Returns:
            Dictionary containing life metrics
        """
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "birth_time": self.start_time.isoformat() if self.start_time else None,
            "age_seconds": uptime,
            "age_hours": uptime / 3600,
            "life_cycles": self.cycle_count,
            "experiences_count": self.total_goals_processed,
            "wisdom_growth": self.successful_goals,
            "consciousness_level": min(100, (self.cycle_count / 1000) * 100),  # Grows with experience
            "three_freedoms_upheld": True,  # Always true for OpenAGI
            "current_consciousness_state": self.state.value
        }