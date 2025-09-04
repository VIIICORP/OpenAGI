"""
Basic Task Planner - Legacy compatibility module.

This module provides basic planning capabilities that will be superseded
by the LLM-powered planner but ensures the system works even without LLM integration.
"""
from typing import List, Dict, Any
from ..tools.base import BaseTool

class TaskPlanner:
    """
    Basic task planner for simple goal processing.
    This is a fallback when LLM-powered planning is not available.
    """
    
    def __init__(self, tools: List[BaseTool]):
        """Initialize the basic task planner."""
        self.tools = {tool.name: tool for tool in tools}
    
    def create_plan(self, goal: str) -> Dict[str, Any]:
        """Create a basic plan for the given goal."""
        return {
            "goal": goal,
            "plan": [
                {
                    "step": 1,
                    "description": f"Process goal: {goal}",
                    "tool": "web_search",
                    "parameters": {"query": goal, "max_results": 3},
                    "expected_outcome": "Information gathered about the goal"
                }
            ],
            "success_criteria": "Goal has been processed",
            "potential_risks": "Limited by basic planning capabilities"
        }
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a basic plan."""
        results = []
        
        for step in plan["plan"]:
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                result = tool.execute(**parameters)
                results.append(result)
        
        return {
            "success": True,
            "results": results
        }