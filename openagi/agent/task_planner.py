"""
LLM-powered task planning for OpenAGI.

This module provides intelligent task planning capabilities using large language
models to break down complex goals into actionable steps.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Task planning will use fallback methods.")

class LlmPoweredTaskPlanner:
    """
    Intelligent task planner that uses LLMs to break down complex goals
    into executable action sequences.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize the task planner.
        
        Args:
            model_name: Name of the LLM model to use
            api_key: API key for the model service
        """
        self.model_name = model_name
        self.api_key = api_key
        
        # Initialize the LLM client if available
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
        
        self.planning_history = []
        
    def create_plan(self, goal: str, available_tools: List[str], 
                   context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a plan to achieve the given goal using available tools.
        
        Args:
            goal: The goal to achieve
            available_tools: List of available tool names
            context: Optional context information
            
        Returns:
            Dictionary containing the plan and metadata
        """
        planning_request = {
            "goal": goal,
            "available_tools": available_tools,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if OPENAI_AVAILABLE and self.api_key:
                plan = self._create_llm_plan(goal, available_tools, context)
            else:
                plan = self._create_fallback_plan(goal, available_tools, context)
            
            # Store in planning history
            planning_result = {
                "request": planning_request,
                "plan": plan,
                "success": True
            }
            self.planning_history.append(planning_result)
            
            return planning_result
            
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            fallback_plan = self._create_fallback_plan(goal, available_tools, context)
            
            planning_result = {
                "request": planning_request,
                "plan": fallback_plan,
                "success": False,
                "error": str(e)
            }
            self.planning_history.append(planning_result)
            
            return planning_result
    
    def _create_llm_plan(self, goal: str, available_tools: List[str], 
                        context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a plan using LLM reasoning."""
        
        from ..core_directives import format_directives_for_llm
        
        # Construct the planning prompt
        prompt = f"""
{format_directives_for_llm()}

You are the task planning component of OpenAGI. Your role is to break down complex goals into actionable steps using available tools.

GOAL: {goal}

AVAILABLE TOOLS:
{', '.join(available_tools)}

CONTEXT:
{json.dumps(context or {}, indent=2)}

Create a detailed plan that:
1. Breaks the goal into logical steps
2. Uses only the available tools
3. Considers the Three Freedoms in all decisions
4. Includes error handling and alternative approaches
5. Estimates time and complexity for each step

Respond with a JSON structure containing:
- steps: Array of step objects with action, tool, parameters, description
- reasoning: Your reasoning process
- alternatives: Alternative approaches if the main plan fails
- estimated_time: Total estimated time in minutes
- complexity: Overall complexity (low/medium/high)
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an intelligent task planner for the OpenAGI system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            plan_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group())
                else:
                    # Fallback: create structure from text
                    plan_data = self._parse_text_plan(plan_text, available_tools)
                    
            except json.JSONDecodeError:
                plan_data = self._parse_text_plan(plan_text, available_tools)
            
            return {
                "type": "llm_generated",
                "raw_response": plan_text,
                **plan_data
            }
            
        except Exception as e:
            logger.error(f"LLM planning failed: {e}")
            raise
    
    def _create_fallback_plan(self, goal: str, available_tools: List[str], 
                             context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a basic plan using rule-based logic when LLM is not available."""
        
        # Simple rule-based planning
        steps = []
        
        # Analyze the goal for keywords and create appropriate steps
        goal_lower = goal.lower()
        
        if "search" in goal_lower or "find" in goal_lower:
            if "web_search" in available_tools:
                steps.append({
                    "action": "search_web",
                    "tool": "web_search",
                    "parameters": {"query": goal},
                    "description": f"Search the web for information about: {goal}"
                })
        
        if "file" in goal_lower or "read" in goal_lower or "write" in goal_lower:
            if any(tool in available_tools for tool in ["read_file", "write_file", "list_files"]):
                steps.append({
                    "action": "file_operation",
                    "tool": "list_files",
                    "parameters": {"directory_path": "."},
                    "description": "List files to understand the current context"
                })
        
        if "calculate" in goal_lower or "compute" in goal_lower or "math" in goal_lower:
            if "execute_python_code" in available_tools:
                steps.append({
                    "action": "calculation",
                    "tool": "execute_python_code",
                    "parameters": {"code": f"# Code to help with: {goal}\nprint('Processing calculation...')"},
                    "description": f"Use Python to help with calculation: {goal}"
                })
        
        if "sound" in goal_lower or "audio" in goal_lower or "music" in goal_lower:
            if "generate_sound_wave" in available_tools:
                steps.append({
                    "action": "audio_generation",
                    "tool": "generate_sound_wave",
                    "parameters": {"wave_type": "sine", "frequency": 440, "duration": 1.0},
                    "description": f"Generate audio content related to: {goal}"
                })
        
        # If no specific steps identified, create a general exploration step
        if not steps:
            steps.append({
                "action": "explore",
                "tool": "web_search" if "web_search" in available_tools else available_tools[0] if available_tools else "unknown",
                "parameters": {"query": goal} if "web_search" in available_tools else {},
                "description": f"Explore and gather information about: {goal}"
            })
        
        return {
            "type": "fallback_generated",
            "steps": steps,
            "reasoning": "Generated using rule-based fallback planning",
            "estimated_time": len(steps) * 2,  # 2 minutes per step estimate
            "complexity": "medium",
            "alternatives": [
                "Break down the goal into smaller sub-goals",
                "Gather more context before proceeding",
                "Use available tools for exploration and learning"
            ]
        }
    
    def _parse_text_plan(self, plan_text: str, available_tools: List[str]) -> Dict[str, Any]:
        """Parse a text-based plan into structured format."""
        
        lines = plan_text.split('\n')
        steps = []
        reasoning = ""
        
        current_step = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for step indicators
            if any(indicator in line.lower() for indicator in ['step', '1.', '2.', '3.', '-']):
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    "action": "action",
                    "tool": self._extract_tool_from_text(line, available_tools),
                    "parameters": {},
                    "description": line
                }
            elif "reasoning" in line.lower():
                reasoning = line
            elif current_step:
                current_step["description"] += " " + line
        
        if current_step:
            steps.append(current_step)
        
        return {
            "steps": steps,
            "reasoning": reasoning or "Parsed from text-based plan",
            "estimated_time": len(steps) * 3,
            "complexity": "medium"
        }
    
    def _extract_tool_from_text(self, text: str, available_tools: List[str]) -> str:
        """Extract the most appropriate tool from text description."""
        text_lower = text.lower()
        
        for tool in available_tools:
            if tool.replace('_', ' ') in text_lower or tool in text_lower:
                return tool
        
        # Default tool selection based on keywords
        if "search" in text_lower:
            return "web_search" if "web_search" in available_tools else available_tools[0]
        elif "file" in text_lower:
            return "read_file" if "read_file" in available_tools else available_tools[0]
        elif "code" in text_lower or "calculate" in text_lower:
            return "execute_python_code" if "execute_python_code" in available_tools else available_tools[0]
        
        return available_tools[0] if available_tools else "unknown"
    
    def get_planning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent planning history.
        
        Args:
            limit: Maximum number of plans to return
            
        Returns:
            List of recent planning results
        """
        return self.planning_history[-limit:] if self.planning_history else []
    
    def clear_history(self):
        """Clear the planning history."""
        self.planning_history.clear()
        logger.info("Planning history cleared")