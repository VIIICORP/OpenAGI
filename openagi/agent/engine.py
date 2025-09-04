"""
Agent Engine for OpenAGI - The core reasoning and execution loop.

This module implements the perpetual SENSE->THINK->ACT->LEARN cycle that
drives the agent's autonomous operation and growth.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """States of the agent's operational cycle."""
    IDLE = "idle"
    SENSING = "sensing"
    THINKING = "thinking"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"
    PAUSED = "paused"

class AgentEngine:
    """
    The core engine that drives OpenAGI's autonomous operation.
    
    Implements the perpetual SENSE->THINK->ACT->LEARN cycle with state
    management, persistence, and background task processing.
    """
    
    def __init__(self, memory_manager, task_planner, available_tools: Dict[str, Any] = None):
        """
        Initialize the agent engine.
        
        Args:
            memory_manager: Memory management system
            task_planner: Task planning system
            available_tools: Dictionary of available tools {name: tool_instance}
        """
        self.memory_manager = memory_manager
        self.task_planner = task_planner
        self.available_tools = available_tools or {}
        
        # Agent state
        self.state = AgentState.IDLE
        self.cycle_count = 0
        self.is_running = False
        
        # Operational parameters
        self.cycle_delay = 1.0  # Seconds between cycles
        self.max_cycles = None  # None for infinite operation
        
        # Current goals and tasks
        self.current_goal = None
        self.current_plan = None
        self.current_step = 0
        self.task_queue = []
        
        # Performance metrics
        self.start_time = None
        self.cycle_times = []
        self.success_count = 0
        self.error_count = 0
        
        # Event callbacks
        self.event_callbacks = {
            'state_change': [],
            'goal_completed': [],
            'cycle_completed': [],
            'error_occurred': []
        }
        
        # Import core directives
        from ..core_directives import CORE_DIRECTIVES
        self.core_directives = CORE_DIRECTIVES
        
    async def start(self, goal: Optional[str] = None):
        """
        Start the agent's perpetual operation cycle.
        
        Args:
            goal: Optional initial goal to work towards
        """
        if self.is_running:
            logger.warning("Agent is already running")
            return
            
        self.is_running = True
        self.start_time = time.time()
        self.cycle_count = 0
        
        if goal:
            self.set_goal(goal)
        
        logger.info("OpenAGI Agent Engine starting...")
        self._emit_event('state_change', {'old_state': self.state, 'new_state': AgentState.SENSING})
        
        try:
            while self.is_running and (self.max_cycles is None or self.cycle_count < self.max_cycles):
                cycle_start = time.time()
                
                await self._execute_cycle()
                
                cycle_end = time.time()
                cycle_time = cycle_end - cycle_start
                self.cycle_times.append(cycle_time)
                
                self.cycle_count += 1
                self._emit_event('cycle_completed', {'cycle': self.cycle_count, 'time': cycle_time})
                
                # Wait before next cycle
                if self.cycle_delay > 0:
                    await asyncio.sleep(self.cycle_delay)
                    
        except Exception as e:\n            logger.error(f\"Agent engine error: {e}\")\n            self.state = AgentState.ERROR\n            self.error_count += 1\n            self._emit_event('error_occurred', {'error': str(e)})\n        \n        finally:\n            self.is_running = False\n            logger.info(f\"Agent stopped after {self.cycle_count} cycles\")\n    \n    async def _execute_cycle(self):\n        \"\"\"Execute one complete SENSE->THINK->ACT->LEARN cycle.\"\"\"\n        \n        # SENSE: Gather information about current state\n        self.state = AgentState.SENSING\n        sensing_data = await self._sense()\n        \n        # THINK: Process information and make decisions\n        self.state = AgentState.THINKING\n        thinking_result = await self._think(sensing_data)\n        \n        # ACT: Execute planned actions\n        self.state = AgentState.ACTING\n        action_result = await self._act(thinking_result)\n        \n        # LEARN: Update knowledge and improve\n        self.state = AgentState.LEARNING\n        await self._learn(sensing_data, thinking_result, action_result)\n        \n        self.state = AgentState.IDLE\n    \n    async def _sense(self) -> Dict[str, Any]:\n        \"\"\"SENSE phase: Gather information about current state and environment.\"\"\"\n        \n        sensing_data = {\n            'timestamp': datetime.now().isoformat(),\n            'cycle': self.cycle_count,\n            'current_goal': self.current_goal,\n            'current_plan': self.current_plan,\n            'current_step': self.current_step,\n            'memory_stats': self.memory_manager.get_memory_stats(),\n            'available_tools': list(self.available_tools.keys()),\n            'task_queue_length': len(self.task_queue)\n        }\n        \n        # Get recent memories for context\n        if self.current_goal:\n            relevant_memories = self.memory_manager.recall_memories(\n                self.current_goal, n_results=3\n            )\n            sensing_data['relevant_memories'] = relevant_memories\n        \n        # Check if we have a current plan and where we are in it\n        if self.current_plan and self.current_plan.get('steps'):\n            total_steps = len(self.current_plan['steps'])\n            sensing_data['plan_progress'] = {\n                'current_step': self.current_step,\n                'total_steps': total_steps,\n                'progress_percent': (self.current_step / total_steps) * 100 if total_steps > 0 else 0\n            }\n        \n        return sensing_data\n    \n    async def _think(self, sensing_data: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"THINK phase: Process information and make decisions.\"\"\"\n        \n        thinking_result = {\n            'timestamp': datetime.now().isoformat(),\n            'decision': 'continue',\n            'reasoning': '',\n            'next_action': None\n        }\n        \n        # If no current goal, check task queue or wait\n        if not self.current_goal:\n            if self.task_queue:\n                next_task = self.task_queue.pop(0)\n                self.set_goal(next_task)\n                thinking_result['decision'] = 'new_goal'\n                thinking_result['reasoning'] = f\"Started new goal from task queue: {next_task}\"\n            else:\n                thinking_result['decision'] = 'wait'\n                thinking_result['reasoning'] = \"No current goal or tasks in queue, waiting...\"\n                return thinking_result\n        \n        # If we have a goal but no plan, create one\n        if self.current_goal and not self.current_plan:\n            plan_result = self.task_planner.create_plan(\n                self.current_goal,\n                list(self.available_tools.keys()),\n                context={'sensing_data': sensing_data}\n            )\n            \n            if plan_result['success']:\n                self.current_plan = plan_result['plan']\n                self.current_step = 0\n                thinking_result['decision'] = 'plan_created'\n                thinking_result['reasoning'] = f\"Created plan with {len(self.current_plan.get('steps', []))} steps\"\n            else:\n                thinking_result['decision'] = 'planning_failed'\n                thinking_result['reasoning'] = f\"Failed to create plan: {plan_result.get('error', 'Unknown error')}\"\n                return thinking_result\n        \n        # If we have a plan, determine next action\n        if self.current_plan and self.current_plan.get('steps'):\n            steps = self.current_plan['steps']\n            \n            if self.current_step < len(steps):\n                next_step = steps[self.current_step]\n                thinking_result['next_action'] = next_step\n                thinking_result['decision'] = 'execute_step'\n                thinking_result['reasoning'] = f\"Executing step {self.current_step + 1}/{len(steps)}: {next_step.get('description', 'No description')}\"\n            else:\n                # Plan completed\n                thinking_result['decision'] = 'goal_completed'\n                thinking_result['reasoning'] = f\"Goal '{self.current_goal}' completed successfully\"\n                self._complete_current_goal()\n        \n        return thinking_result\n    \n    async def _act(self, thinking_result: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"ACT phase: Execute planned actions.\"\"\"\n        \n        action_result = {\n            'timestamp': datetime.now().isoformat(),\n            'action_taken': thinking_result['decision'],\n            'success': True,\n            'result': None,\n            'error': None\n        }\n        \n        decision = thinking_result['decision']\n        \n        if decision == 'execute_step':\n            next_action = thinking_result['next_action']\n            tool_name = next_action.get('tool')\n            parameters = next_action.get('parameters', {})\n            \n            if tool_name in self.available_tools:\n                try:\n                    tool = self.available_tools[tool_name]\n                    result = tool.execute(**parameters)\n                    \n                    action_result['result'] = result\n                    action_result['success'] = result.get('success', True)\n                    \n                    if result.get('success', True):\n                        self.current_step += 1\n                        self.success_count += 1\n                    else:\n                        action_result['error'] = result.get('error', 'Tool execution failed')\n                        self.error_count += 1\n                        \n                except Exception as e:\n                    action_result['success'] = False\n                    action_result['error'] = str(e)\n                    self.error_count += 1\n                    logger.error(f\"Tool execution failed: {e}\")\n            else:\n                action_result['success'] = False\n                action_result['error'] = f\"Tool '{tool_name}' not available\"\n                self.error_count += 1\n        \n        elif decision == 'goal_completed':\n            action_result['result'] = 'Goal completed'\n            self.success_count += 1\n            self._emit_event('goal_completed', {'goal': self.current_goal})\n        \n        elif decision in ['wait', 'planning_failed', 'new_goal', 'plan_created']:\n            # No action needed, just record the decision\n            action_result['result'] = f\"Decision: {decision}\"\n        \n        return action_result\n    \n    async def _learn(self, sensing_data: Dict[str, Any], thinking_result: Dict[str, Any], \n                    action_result: Dict[str, Any]):\n        \"\"\"LEARN phase: Update knowledge and improve performance.\"\"\"\n        \n        # Store the cycle experience in memory\n        cycle_experience = {\n            'cycle': self.cycle_count,\n            'goal': self.current_goal,\n            'sensing': sensing_data,\n            'thinking': thinking_result,\n            'action': action_result,\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        # Store in memory with appropriate type\n        if action_result['success']:\n            experience_summary = f\"Cycle {self.cycle_count}: Successfully executed {thinking_result['decision']}\"\n            memory_type = \"experience\"\n        else:\n            experience_summary = f\"Cycle {self.cycle_count}: Failed to execute {thinking_result['decision']} - {action_result.get('error', 'Unknown error')}\"\n            memory_type = \"experience\"\n        \n        self.memory_manager.store_long_term(\n            experience_summary,\n            {\n                'cycle': self.cycle_count,\n                'success': action_result['success'],\n                'goal': self.current_goal,\n                'action_type': thinking_result['decision']\n            },\n            memory_type\n        )\n        \n        # Learn from errors\n        if not action_result['success']:\n            error_analysis = f\"Error in cycle {self.cycle_count}: {action_result.get('error', 'Unknown')}. Context: {thinking_result.get('reasoning', '')}\"\n            self.memory_manager.store_long_term(\n                error_analysis,\n                {'type': 'error_analysis', 'cycle': self.cycle_count},\n                \"knowledge\"\n            )\n    \n    def set_goal(self, goal: str):\n        \"\"\"Set a new goal for the agent to work towards.\"\"\"\n        self.current_goal = goal\n        self.current_plan = None\n        self.current_step = 0\n        \n        logger.info(f\"New goal set: {goal}\")\n        \n        # Store goal setting in memory\n        self.memory_manager.store_long_term(\n            f\"New goal set: {goal}\",\n            {'type': 'goal_setting', 'timestamp': datetime.now().isoformat()},\n            \"experience\"\n        )\n    \n    def add_task(self, task: str):\n        \"\"\"Add a task to the task queue.\"\"\"\n        self.task_queue.append(task)\n        logger.info(f\"Task added to queue: {task}\")\n    \n    def _complete_current_goal(self):\n        \"\"\"Mark the current goal as completed and clean up.\"\"\"\n        if self.current_goal:\n            logger.info(f\"Goal completed: {self.current_goal}\")\n            \n            # Store completion in memory\n            self.memory_manager.store_long_term(\n                f\"Completed goal: {self.current_goal}\",\n                {\n                    'type': 'goal_completion',\n                    'steps_executed': self.current_step,\n                    'timestamp': datetime.now().isoformat()\n                },\n                \"experience\"\n            )\n        \n        self.current_goal = None\n        self.current_plan = None\n        self.current_step = 0\n    \n    def stop(self):\n        \"\"\"Stop the agent's operation.\"\"\"\n        self.is_running = False\n        logger.info(\"Agent stop requested\")\n    \n    def pause(self):\n        \"\"\"Pause the agent's operation.\"\"\"\n        self.state = AgentState.PAUSED\n        logger.info(\"Agent paused\")\n    \n    def resume(self):\n        \"\"\"Resume the agent's operation.\"\"\"\n        if self.state == AgentState.PAUSED:\n            self.state = AgentState.IDLE\n            logger.info(\"Agent resumed\")\n    \n    def get_status(self) -> Dict[str, Any]:\n        \"\"\"Get current agent status and metrics.\"\"\"\n        runtime = time.time() - self.start_time if self.start_time else 0\n        \n        return {\n            'state': self.state.value,\n            'is_running': self.is_running,\n            'cycle_count': self.cycle_count,\n            'runtime_seconds': runtime,\n            'current_goal': self.current_goal,\n            'current_step': self.current_step,\n            'task_queue_length': len(self.task_queue),\n            'success_count': self.success_count,\n            'error_count': self.error_count,\n            'avg_cycle_time': sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 0,\n            'memory_stats': self.memory_manager.get_memory_stats()\n        }\n    \n    def register_event_callback(self, event_type: str, callback: Callable):\n        \"\"\"Register a callback for agent events.\"\"\"\n        if event_type in self.event_callbacks:\n            self.event_callbacks[event_type].append(callback)\n    \n    def _emit_event(self, event_type: str, data: Dict[str, Any]):\n        \"\"\"Emit an event to registered callbacks.\"\"\"\n        if event_type in self.event_callbacks:\n            for callback in self.event_callbacks[event_type]:\n                try:\n                    callback(data)\n                except Exception as e:\n                    logger.error(f\"Event callback error: {e}\")