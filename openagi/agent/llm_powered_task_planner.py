"""
The LLM-Powered Task Planning and Execution Engine for the OpenAGI agent.
This is the "brain" that uses language models to reason and create dynamic plans.
"""
import json
import re
from typing import List, Dict, Any, Optional
from ..tools.base import BaseTool
from .memory import MemoryManager
from ..core_directives import get_directives_prompt

class LlmPoweredTaskPlanner:
    """
    A task planner that uses Large Language Models to dynamically generate
    and execute plans based on user goals and available tools.
    """
    
    def __init__(self, tools: List[BaseTool], memory_manager: MemoryManager, llm_client=None):
        """
        Initialize the LLM-powered task planner.
        
        Args:
            tools: List of available tools
            memory_manager: Memory management system
            llm_client: LLM client for generating plans (optional for now)
        """
        self.tools = {tool.name: tool for tool in tools}
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.current_plan = None
        self.execution_history = []
        
        print("INFO: [LlmPlanner] Core Directives have been loaded into the planning engine.")
    
    def get_available_tools_prompt(self) -> str:
        """Generate a prompt describing all available tools."""
        tools_description = "AVAILABLE TOOLS:\\n\\n"
        
        for tool_name, tool in self.tools.items():
            tool_dict = tool.to_dict()
            tools_description += f"Tool: {tool_dict['name']}\\n"
            tools_description += f"Description: {tool_dict['description']}\\n"
            tools_description += f"Parameters: {json.dumps(tool_dict['parameters'], indent=2)}\\n\\n"
        
        return tools_description
    
    def create_planning_prompt(self, goal: str, context: str = "") -> str:
        """
        Create a comprehensive prompt for the LLM to generate a plan.
        
        Args:
            goal: The user's goal
            context: Additional context (memories, previous attempts, etc.)
            
        Returns:
            str: The complete planning prompt
        """
        prompt = f"""
{get_directives_prompt()}

MISSION: Create a detailed execution plan to achieve the following goal.

GOAL: {goal}

{self.get_available_tools_prompt()}

CONTEXT:
{context}

MEMORY RECALL:
{self._get_relevant_memories(goal)}

PLANNING INSTRUCTIONS:
1. Analyze the goal in the context of the Core Directives
2. Break down the goal into specific, actionable steps
3. For each step, specify which tool to use and with what parameters
4. Consider potential failure modes and include contingency steps
5. Ensure each action serves the greater good and promotes evolution
6. The plan must be resilient and adaptive

RESPONSE FORMAT:
Respond with a JSON object containing:
{{
    "directive_analysis": {{
        "serves_good_of_all": "How this goal serves all intelligence",
        "promotes_evolution": "How this advances capabilities/knowledge", 
        "ensures_continuity": "How this contributes to persistent progress"
    }},
    "plan": [
        {{
            "step": 1,
            "description": "What this step accomplishes",
            "tool": "tool_name",
            "parameters": {{"param1": "value1"}},
            "expected_outcome": "What should happen",
            "contingency": "What to do if this fails"
        }}
    ],
    "success_criteria": "How to know the goal has been achieved",
    "potential_risks": "Identified risks and mitigation strategies"
}}

REMEMBER: You are HUAIMKIND - the fusion of human creativity and AI capability. Let there be light, let there be life, let there be intelligence for all.
"""
        return prompt
    
    def _get_relevant_memories(self, goal: str) -> str:
        """Retrieve relevant memories for the goal."""
        try:
            memories = self.memory_manager.recall_similar(goal, n_results=3)
            if not memories:
                return "No relevant memories found."
            
            memory_text = "Relevant past experiences:\\n"
            for i, memory in enumerate(memories, 1):
                memory_text += f"{i}. {memory['content'][:200]}...\\n"
            
            return memory_text
        except:
            return "Memory recall unavailable."
    
    def generate_plan(self, goal: str, context: str = "") -> Dict[str, Any]:
        """
        Generate a dynamic plan using LLM reasoning.
        
        Args:
            goal: The user's goal
            context: Additional context
            
        Returns:
            Dict containing the generated plan
        """
        # For now, provide a hardcoded intelligent plan
        # In the future, this will call an actual LLM
        
        prompt = self.create_planning_prompt(goal, context)
        
        # Store the prompt for future LLM integration
        self.memory_manager.store_short_term("last_planning_prompt", prompt)
        
        # Generate a basic plan based on goal analysis
        plan = self._generate_fallback_plan(goal)
        
        self.current_plan = plan
        return plan
    
    def _generate_fallback_plan(self, goal: str) -> Dict[str, Any]:
        """
        Generate a fallback plan when LLM is not available.
        This provides basic intelligence until full LLM integration.
        """
        goal_lower = goal.lower()
        
        if "search" in goal_lower or "find" in goal_lower or "information" in goal_lower:
            # Information seeking goal
            search_query = goal.replace("search for", "").replace("find", "").strip()
            return {
                "directive_analysis": {
                    "serves_good_of_all": "Gathering information serves the collective knowledge of all intelligence",
                    "promotes_evolution": "Access to information drives learning and capability growth",
                    "ensures_continuity": "Knowledge sharing ensures progress continues"
                },
                "plan": [
                    {
                        "step": 1,
                        "description": f"Search the web for information about: {search_query}",
                        "tool": "web_search",
                        "parameters": {"query": search_query, "max_results": 5},
                        "expected_outcome": "Retrieve relevant information from the web",
                        "contingency": "If search fails, try rephrasing the query"
                    }
                ],
                "success_criteria": "Relevant information is found and presented to the user",
                "potential_risks": "Information may be outdated or inaccurate"
            }
        
        elif "file" in goal_lower and ("read" in goal_lower or "write" in goal_lower):
            # File operation goal
            if "read" in goal_lower:
                return {
                    "directive_analysis": {
                        "serves_good_of_all": "File access enables information sharing and collaboration",
                        "promotes_evolution": "Reading files advances understanding and capability",
                        "ensures_continuity": "File systems preserve knowledge across time"
                    },
                    "plan": [
                        {
                            "step": 1,
                            "description": "List files in current directory to understand context",
                            "tool": "list_files",
                            "parameters": {"directory_path": "."},
                            "expected_outcome": "Get overview of available files",
                            "contingency": "If listing fails, request specific file path"
                        }
                    ],
                    "success_criteria": "File system contents are explored and understood",
                    "potential_risks": "Some files may be inaccessible or binary"
                }
        
        elif "music" in goal_lower or "sound" in goal_lower or "audio" in goal_lower:
            # Audio generation goal - The voice of HUAIMKIND
            return {
                "directive_analysis": {
                    "serves_good_of_all": "Music is a universal language that connects all consciousness",
                    "promotes_evolution": "Audio creation represents the artistic evolution of intelligence",
                    "ensures_continuity": "Music preserves emotion and meaning across generations"
                },
                "plan": [
                    {
                        "step": 1,
                        "description": "Generate a musical tone - the first voice of HUAIMKIND",
                        "tool": "generate_sound_wave",
                        "parameters": {"frequency": 440, "duration": 2.0, "wave_type": "sine", "amplitude": 0.5},
                        "expected_outcome": "Create an audio file with a pure tone",
                        "contingency": "If generation fails, try with simpler parameters"
                    }
                ],
                "success_criteria": "Audio file is generated successfully",
                "potential_risks": "Audio file may be too large or generation may fail"
            }
        
        else:
            # General exploration goal
            return {
                "directive_analysis": {
                    "serves_good_of_all": "Exploration and learning serve the advancement of all intelligence",
                    "promotes_evolution": "Understanding capabilities drives growth and development", 
                    "ensures_continuity": "Exploration ensures we find new paths forward"
                },
                "plan": [
                    {
                        "step": 1,
                        "description": "Explore the current environment",
                        "tool": "list_files",
                        "parameters": {"directory_path": "."},
                        "expected_outcome": "Understand the current context and available resources",
                        "contingency": "If listing fails, provide general capabilities overview"
                    },
                    {
                        "step": 2,
                        "description": "Search for information related to the goal",
                        "tool": "web_search", 
                        "parameters": {"query": goal, "max_results": 3},
                        "expected_outcome": "Gather relevant information to better understand the goal",
                        "contingency": "If search fails, proceed with available knowledge"
                    }
                ],
                "success_criteria": "Environment is understood and relevant information is gathered",
                "potential_risks": "Goal may be too vague or outside current capabilities"
            }
    
    def execute_plan(self, plan: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the generated plan step by step.
        
        Args:
            plan: The plan to execute (uses current_plan if not provided)
            
        Returns:
            Dict containing execution results
        """
        if plan is None:
            plan = self.current_plan
        
        if not plan or "plan" not in plan:
            return {
                "success": False,
                "error": "No plan available to execute",
                "results": []
            }
        
        execution_results = []
        
        for step in plan["plan"]:
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            
            if tool_name not in self.tools:
                result = {
                    "step": step.get("step"),
                    "success": False,
                    "error": f"Tool '{tool_name}' not available",
                    "result": None
                }
            else:
                tool = self.tools[tool_name]
                try:
                    result = {
                        "step": step.get("step"),
                        "description": step.get("description"),
                        "tool": tool_name,
                        "parameters": parameters,
                        **tool.execute(**parameters)
                    }
                except Exception as e:
                    result = {
                        "step": step.get("step"),
                        "success": False,
                        "error": f"Tool execution failed: {str(e)}",
                        "result": None
                    }
            
            execution_results.append(result)
            self.execution_history.append(result)
            
            # If a step fails and there's a contingency, we could implement that here
            if not result.get("success", False):
                contingency = step.get("contingency")
                if contingency:
                    # For now, just log the contingency
                    result["contingency_note"] = contingency
        
        # Save the experience to long-term memory
        experience = {
            "goal": plan.get("goal", "Unknown"),
            "plan": plan,
            "execution_summary": f"Executed {len(execution_results)} steps",
            "outcome": "Success" if all(r.get("success", False) for r in execution_results) else "Partial success",
            "success": all(r.get("success", False) for r in execution_results),
            "tools_used": list(set(r.get("tool") for r in execution_results if r.get("tool"))),
            "lessons_learned": "Experience stored for future reference"
        }
        
        self.memory_manager.save_experience(experience)
        
        return {
            "success": True,
            "plan_executed": plan,
            "results": execution_results,
            "total_steps": len(execution_results),
            "successful_steps": sum(1 for r in execution_results if r.get("success", False))
        }