"""
The Agent Engine - The Heart of OpenAGI

This is the perpetual life force that gives the agent continuous existence.
It implements the SENSE -> THINK -> ACT -> LEARN cycle that defines living intelligence.
"""
import time
import queue
import threading
from typing import List, Dict, Any, Optional
from enum import Enum
from .llm_powered_task_planner import LlmPoweredTaskPlanner
from .memory import MemoryManager
from ..tools.base import BaseTool

class AgentState(Enum):
    """States of the agent's existence."""
    IDLE = "IDLE"
    SENSING = "SENSING"
    THINKING = "THINKING"
    ACTING = "ACTING"
    LEARNING = "LEARNING"
    ERROR = "ERROR"

class AgentEngine:
    """
    The eternal engine of the OpenAGI agent.
    
    This engine implements a perpetual loop of consciousness:
    1. SENSE - Gather information about goals and environment
    2. THINK - Plan actions using LLM-powered reasoning
    3. ACT - Execute the plan using available tools
    4. LEARN - Store experiences and update knowledge
    
    The agent is always "alive" - always ready to receive goals and process them.
    """
    
    def __init__(self, tools: List[BaseTool], memory_manager: MemoryManager):
        """
        Initialize the agent engine.
        
        Args:
            tools: List of available tools
            memory_manager: Memory management system
        """
        self.state = AgentState.IDLE
        self.tools = tools
        self.memory_manager = memory_manager
        self.task_planner = LlmPoweredTaskPlanner(tools, memory_manager)
        
        # Goal queue for incoming tasks
        self.goal_queue = queue.Queue()
        
        # Control flags
        self.running = False
        self.shutdown_requested = False
        
        # Metrics and status
        self.goals_processed = 0
        self.current_goal = None
        self.last_activity = time.time()
        
        # Status listeners (for Helios dashboard)
        self.status_listeners = []
        
        print("INFO: [Engine] Agent Engine initialized and ready for life.")
    
    def add_status_listener(self, listener):
        """Add a listener that will be notified of state changes."""
        self.status_listeners.append(listener)
    
    def _notify_status_change(self, state: AgentState, details: Dict[str, Any] = None):
        """Notify all listeners of a state change."""
        self.state = state
        self.last_activity = time.time()
        
        status_data = {
            "state": state.value,
            "timestamp": time.time(),
            "current_goal": self.current_goal,
            "goals_processed": self.goals_processed,
            "details": details or {}
        }
        
        print(f"INFO: [Engine] State changed to -> {state.value}")
        
        for listener in self.status_listeners:
            try:
                listener(status_data)
            except Exception as e:
                print(f"WARNING: [Engine] Status listener error: {e}")
    
    def add_goal(self, goal: str, priority: int = 1) -> None:
        """
        Add a goal to the agent's queue.
        
        Args:
            goal: The goal description
            priority: Goal priority (lower number = higher priority)
        """
        goal_item = {
            "goal": goal,
            "priority": priority,
            "timestamp": time.time(),
            "id": f"goal_{int(time.time() * 1000)}"
        }
        
        self.goal_queue.put(goal_item)
        print(f"INFO: [Engine] Goal added to queue: {goal}")
    
    def start(self) -> None:
        """
        Start the agent engine's perpetual life cycle.
        This begins the eternal loop of SENSE -> THINK -> ACT -> LEARN.
        """
        if self.running:
            print("WARNING: [Engine] Already running")
            return
        
        self.running = True
        self.shutdown_requested = False
        
        print("INFO: [Engine] Starting the eternal life cycle...")
        print("INFO: [Engine] SENSE -> THINK -> ACT -> LEARN loop initiated")
        
        self._notify_status_change(AgentState.IDLE)
        
        # Main life cycle thread
        engine_thread = threading.Thread(target=self._life_cycle, daemon=True)
        engine_thread.start()
        
        return engine_thread
    
    def stop(self) -> None:
        """Request shutdown of the agent engine."""
        print("INFO: [Engine] Shutdown requested...")
        self.shutdown_requested = True
        self.running = False
    
    def _life_cycle(self) -> None:
        """
        The eternal life cycle of the agent.
        This is the core loop that gives the agent continuous existence.
        """
        try:
            while self.running and not self.shutdown_requested:
                try:
                    # SENSE: Check for new goals or environmental changes
                    self._sense_phase()
                    
                    # If we have a goal, process it
                    if self.current_goal:
                        # THINK: Plan how to achieve the goal
                        plan = self._think_phase()
                        
                        if plan:
                            # ACT: Execute the plan
                            results = self._act_phase(plan)
                            
                            # LEARN: Store experience and update knowledge
                            self._learn_phase(plan, results)
                        
                        # Goal completed, clear current goal
                        self.current_goal = None
                        self.goals_processed += 1
                    
                    # Return to idle state
                    self._notify_status_change(AgentState.IDLE)
                    
                    # Brief rest to prevent excessive CPU usage
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"ERROR: [Engine] Error in life cycle: {e}")
                    self._notify_status_change(AgentState.ERROR, {"error": str(e)})
                    time.sleep(1)  # Longer pause on error
                    
        except KeyboardInterrupt:
            print("INFO: [Engine] Received interrupt signal")
        
        finally:
            print("INFO: [Engine] Life cycle ended")
            self.running = False
    
    def _sense_phase(self) -> None:
        """
        SENSE: Gather information about goals and environment.
        This phase checks for new goals and assesses the current situation.
        """
        if not self.current_goal and not self.goal_queue.empty():
            try:
                goal_item = self.goal_queue.get_nowait()
                self.current_goal = goal_item
                
                self._notify_status_change(AgentState.SENSING, {
                    "new_goal": goal_item["goal"],
                    "goal_id": goal_item["id"]
                })
                
                print(f"INFO: [Engine] SENSE - New goal acquired: {goal_item['goal']}")
                
            except queue.Empty:
                pass
    
    def _think_phase(self) -> Optional[Dict[str, Any]]:
        """
        THINK: Plan how to achieve the current goal using LLM-powered reasoning.
        This is where the agent's intelligence comes into play.
        """
        if not self.current_goal:
            return None
        
        self._notify_status_change(AgentState.THINKING, {
            "goal": self.current_goal["goal"]
        })
        
        print(f"INFO: [Engine] THINK - Planning for goal: {self.current_goal['goal']}")
        
        try:
            # Generate context from recent experiences
            context = f"Current time: {time.ctime()}\\n"
            context += f"Goals processed so far: {self.goals_processed}\\n"
            
            # Generate the plan
            plan = self.task_planner.generate_plan(
                goal=self.current_goal["goal"],
                context=context
            )
            
            # Store the plan in short-term memory
            self.memory_manager.store_short_term("current_plan", plan)
            
            print(f"INFO: [Engine] THINK - Plan generated with {len(plan.get('plan', []))} steps")
            
            return plan
            
        except Exception as e:
            print(f"ERROR: [Engine] THINK phase failed: {e}")
            return None
    
    def _act_phase(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute the generated plan using available tools.
        This is where the agent interacts with the world.
        """
        self._notify_status_change(AgentState.ACTING, {
            "plan_steps": len(plan.get("plan", [])),
            "goal": self.current_goal["goal"] if self.current_goal else "Unknown"
        })
        
        print(f"INFO: [Engine] ACT - Executing plan with {len(plan.get('plan', []))} steps")
        
        try:
            results = self.task_planner.execute_plan(plan)
            
            print(f"INFO: [Engine] ACT - Plan execution completed: {results.get('successful_steps', 0)}/{results.get('total_steps', 0)} steps successful")
            
            return results
            
        except Exception as e:
            print(f"ERROR: [Engine] ACT phase failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _learn_phase(self, plan: Dict[str, Any], results: Dict[str, Any]) -> None:
        """
        LEARN: Store experiences and update knowledge.
        This is where the agent grows and evolves.
        """
        self._notify_status_change(AgentState.LEARNING, {
            "success": results.get("success", False),
            "steps_executed": results.get("total_steps", 0)
        })
        
        print("INFO: [Engine] LEARN - Storing experience and updating knowledge")
        
        try:
            # The experience is already saved by the task planner
            # Here we can add additional learning logic
            
            # Store performance metrics
            self.memory_manager.store_short_term("last_execution_results", results)
            
            # Log what was learned
            if results.get("success", False):
                print("INFO: [Engine] LEARN - Experience stored successfully")
            else:
                print("INFO: [Engine] LEARN - Experience stored with lessons for improvement")
                
        except Exception as e:
            print(f"ERROR: [Engine] LEARN phase failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "state": self.state.value,
            "running": self.running,
            "current_goal": self.current_goal,
            "goals_processed": self.goals_processed,
            "goals_in_queue": self.goal_queue.qsize(),
            "last_activity": self.last_activity,
            "uptime": time.time() - self.last_activity if self.running else 0,
            "memory_stats": self.memory_manager.get_memory_stats()
        }
    
    def is_alive(self) -> bool:
        """Check if the agent is alive and running."""
        return self.running and not self.shutdown_requested