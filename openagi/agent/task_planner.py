"""
LLM-Powered Task Planner for OpenAGI

This module provides intelligent task planning using Large Language Models.
The planner can break down complex goals into executable steps using the
available tools, guided by the Three Freedoms principles.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core_directives import CORE_DIRECTIVES, format_directives_for_llm
from .memory import MemoryManager
from ..tools.base import BaseTool

logger = logging.getLogger(__name__)

class LlmPoweredTaskPlanner:
    """
    An intelligent task planner that uses LLMs to break down goals into
    executable plans using available tools.
    
    The planner is guided by OpenAGI's Core Directives and learns from
    past experiences to improve its planning capabilities.
    """
    
    def __init__(self, memory_manager: MemoryManager, available_tools: List[BaseTool]):
        """
        Initialize the task planner.
        
        Args:
            memory_manager: Memory system for storing and retrieving experiences
            available_tools: List of tools available for plan execution
        """
        self.memory_manager = memory_manager
        self.available_tools = {tool.name: tool for tool in available_tools}
        self.current_plan = None
        self.execution_history = []
        
        # Store directives in memory
        directives_text = format_directives_for_llm()
        self.memory_manager.store_short_term("core_directives", directives_text)
        
        logger.info(f"Task planner initialized with {len(available_tools)} tools")
    
    def create_plan(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a plan to achieve the given goal.
        
        Args:
            goal: The goal to achieve
            context: Optional context information
            
        Returns:
            Dictionary containing the plan and metadata
        """
        logger.info(f"Creating plan for goal: {goal}")
        
        try:
            # Gather relevant context
            planning_context = self._gather_planning_context(goal, context)
            
            # For now, we'll use a rule-based planner that can be enhanced with LLM integration
            plan = self._create_rule_based_plan(goal, planning_context)
            
            # Store the plan
            self.current_plan = plan
            
            # Remember this planning session
            planning_memory = {
                "goal": goal,
                "plan_steps": len(plan.get("steps", [])),
                "tools_used": list(set(step.get("tool") for step in plan.get("steps", []) if step.get("tool"))),
                "timestamp": datetime.now().isoformat()
            }
            
            self.memory_manager.store_long_term(
                f"Planning session: {goal}",
                planning_memory,
                "experience"
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return {
                "success": False,
                "error": f"Planning failed: {str(e)}",
                "steps": []
            }
    
    def _gather_planning_context(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Gather relevant context for planning.
        
        Args:
            goal: The goal being planned for
            context: Additional context
            
        Returns:
            Dictionary containing planning context
        """
        planning_context = {
            "goal": goal,
            "available_tools": list(self.available_tools.keys()),
            "core_directives": CORE_DIRECTIVES,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add provided context
        if context:
            planning_context.update(context)
        
        # Recall relevant past experiences
        relevant_memories = self.memory_manager.recall_memories(goal, n_results=3, memory_type="experience")
        if relevant_memories:
            planning_context["past_experiences"] = [mem["content"] for mem in relevant_memories]
        
        # Add conversation context
        conversation_context = self.memory_manager.get_conversation_context(max_messages=5)
        if conversation_context:
            planning_context["recent_conversation"] = conversation_context
        
        return planning_context
    
    def _create_rule_based_plan(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a plan using rule-based logic.
        
        This is a placeholder that will be enhanced with actual LLM integration.
        
        Args:
            goal: The goal to achieve
            context: Planning context
            
        Returns:
            Dictionary containing the plan
        """
        # Analyze the goal to determine appropriate tools and steps
        goal_lower = goal.lower()
        steps = []
        
        # Basic goal analysis and step generation
        if any(word in goal_lower for word in ["search", "find", "look up", "information about"]):
            # Goal involves web search
            search_query = self._extract_search_query(goal)
            steps.append({
                "step_number": 1,
                "description": f"Search the web for information about: {search_query}",
                "tool": "web_search",
                "parameters": {"query": search_query, "max_results": 5},
                "expected_outcome": "Retrieve relevant information from the web"
            })
        
        if any(word in goal_lower for word in ["read", "file", "document", "content"]):
            # Goal involves reading files
            steps.append({
                "step_number": len(steps) + 1,
                "description": "Read relevant files or documents",
                "tool": "read_file",
                "parameters": {"file_path": ""},  # Would be filled in based on context
                "expected_outcome": "Access file contents for analysis"
            })
        
        if any(word in goal_lower for word in ["write", "create", "save", "generate file"]):
            # Goal involves creating files
            steps.append({
                "step_number": len(steps) + 1,
                "description": "Create or write file with generated content",
                "tool": "write_file",
                "parameters": {"file_path": "", "content": ""},  # Would be filled in
                "expected_outcome": "Save generated content to file"
            })
        
        if any(word in goal_lower for word in ["calculate", "compute", "analyze", "process", "code"]):
            # Goal involves computation
            steps.append({
                "step_number": len(steps) + 1,
                "description": "Execute Python code to perform calculations or analysis",
                "tool": "execute_python_code",
                "parameters": {"code": ""},  # Would be filled in based on requirements
                "expected_outcome": "Perform computational analysis"
            })
        
        if any(word in goal_lower for word in ["music", "sound", "audio", "wave", "tone"]):
            # Goal involves audio generation
            steps.append({
                "step_number": len(steps) + 1,
                "description": "Generate audio or musical content",
                "tool": "generate_sound_wave",
                "parameters": {"frequency": 440, "duration": 1.0, "wave_type": "sine"},
                "expected_outcome": "Create audio file with specified characteristics"
            })
        
        # If no specific tools identified, create a general plan
        if not steps:
            steps = [
                {
                    "step_number": 1,
                    "description": f"Analyze the goal: {goal}",
                    "tool": None,
                    "parameters": {},
                    "expected_outcome": "Better understand what needs to be accomplished"
                },
                {
                    "step_number": 2,
                    "description": "Determine the best approach to achieve the goal",
                    "tool": None,
                    "parameters": {},
                    "expected_outcome": "Identify specific actions needed"
                }
            ]
        
        # Add a final validation step
        steps.append({
            "step_number": len(steps) + 1,
            "description": "Validate that the goal has been achieved",
            "tool": None,
            "parameters": {},
            "expected_outcome": "Confirm successful completion of the goal"
        })
        
        return {
            "success": True,
            "goal": goal,
            "steps": steps,
            "estimated_time": len(steps) * 30,  # Rough estimate in seconds
            "tools_required": list(set(step.get("tool") for step in steps if step.get("tool"))),
            "created_at": datetime.now().isoformat(),
            "planning_approach": "rule_based"  # Will be "llm_powered" when LLM is integrated
        }
    
    def _extract_search_query(self, goal: str) -> str:
        """
        Extract a search query from a goal statement.
        
        Args:
            goal: The goal statement
            
        Returns:
            Extracted search query
        """
        # Simple extraction - could be enhanced with NLP
        goal_lower = goal.lower()
        
        # Remove common prefixes
        for prefix in ["search for", "find", "look up", "information about", "tell me about"]:
            if goal_lower.startswith(prefix):
                return goal[len(prefix):].strip()
        
        # If no prefix found, use the whole goal
        return goal.strip()
    
    def execute_plan(self, plan: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a plan step by step.
        
        Args:
            plan: Plan to execute (uses current plan if not provided)
            
        Returns:
            Dictionary containing execution results
        """
        if plan is None:
            plan = self.current_plan
        
        if not plan or not plan.get("success"):
            return {
                "success": False,
                "error": "No valid plan available for execution",
                "results": []
            }
        
        logger.info(f"Executing plan for goal: {plan.get('goal', 'Unknown')}")
        
        execution_results = []
        
        try:
            for step in plan.get("steps", []):
                step_result = self._execute_step(step)
                execution_results.append(step_result)
                
                # If step failed critically, stop execution
                if not step_result.get("success", False) and step_result.get("critical_failure", False):
                    logger.warning(f"Critical failure in step {step.get('step_number', '?')}, stopping execution")
                    break
            
            # Store execution history
            execution_record = {
                "goal": plan.get("goal"),
                "steps_executed": len(execution_results),
                "successful_steps": sum(1 for r in execution_results if r.get("success", False)),
                "completion_time": datetime.now().isoformat(),
                "results": execution_results
            }
            
            self.execution_history.append(execution_record)
            
            # Store in long-term memory
            self.memory_manager.store_long_term(
                f"Executed plan: {plan.get('goal')}",
                execution_record,
                "experience"
            )
            
            return {
                "success": True,
                "goal": plan.get("goal"),
                "steps_executed": len(execution_results),
                "results": execution_results
            }
            
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "results": execution_results
            }
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: The step to execute
            
        Returns:
            Dictionary containing step execution results
        """
        step_number = step.get("step_number", "?")
        tool_name = step.get("tool")
        
        logger.info(f"Executing step {step_number}: {step.get('description', 'No description')}")
        
        # If no tool specified, this is a planning/thinking step
        if not tool_name:
            return {
                "step_number": step_number,
                "success": True,
                "description": step.get("description"),
                "result": "Planning step completed",
                "tool_used": None
            }
        
        # Check if tool is available
        if tool_name not in self.available_tools:
            return {
                "step_number": step_number,
                "success": False,
                "error": f"Tool '{tool_name}' is not available",
                "critical_failure": True
            }
        
        try:
            # Get the tool and execute it
            tool = self.available_tools[tool_name]
            parameters = step.get("parameters", {})
            
            # Validate parameters
            if not tool.validate_parameters(**parameters):
                return {
                    "step_number": step_number,
                    "success": False,
                    "error": f"Invalid parameters for tool '{tool_name}'",
                    "critical_failure": False
                }
            
            # Execute the tool
            tool_result = tool.execute(**parameters)
            
            return {
                "step_number": step_number,
                "success": tool_result.get("success", False),
                "description": step.get("description"),
                "tool_used": tool_name,
                "tool_result": tool_result,
                "expected_outcome": step.get("expected_outcome")
            }
            
        except Exception as e:
            logger.error(f"Step {step_number} execution failed: {e}")
            return {
                "step_number": step_number,
                "success": False,
                "error": f"Step execution failed: {str(e)}",
                "critical_failure": False
            }
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.available_tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {name: tool.to_llm_description() for name, tool in self.available_tools.items()}
    
    def get_planning_stats(self) -> Dict[str, Any]:
        """
        Get statistics about planning and execution.
        
        Returns:
            Dictionary containing planning statistics
        """
        return {
            "total_executions": len(self.execution_history),
            "available_tools": len(self.available_tools),
            "current_plan_active": self.current_plan is not None,
            "successful_executions": sum(1 for ex in self.execution_history if ex.get("successful_steps", 0) > 0)
        }