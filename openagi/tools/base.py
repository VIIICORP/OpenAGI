"""
Base class for all tools that the OpenAGI agent can use.

This module defines the interface that all tools must implement to be
usable by the agent's planning and execution system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseTool(ABC):
    """
    Abstract base class for all OpenAGI tools.
    
    Tools are the agent's way of interacting with the world. Each tool
    encapsulates a specific capability and provides a standardized interface
    for the agent to use.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        Return the parameters this tool accepts.
        
        Should be in JSON Schema format for LLM understanding.
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Parameters for tool execution
            
        Returns:
            Dictionary containing the result and any relevant metadata
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate that the provided parameters are correct.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # Basic validation - override for more complex validation
        required_params = self.get_required_parameters()
        return all(param in kwargs for param in required_params)
    
    def get_required_parameters(self) -> List[str]:
        """
        Get the list of required parameters.
        
        Returns:
            List of required parameter names
        """
        params = self.parameters.get("properties", {})
        required = self.parameters.get("required", [])
        return required
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        """
        Get example usages of this tool.
        
        Returns:
            List of example usage dictionaries
        """
        return []
    
    def get_safety_notes(self) -> List[str]:
        """
        Get safety considerations for this tool.
        
        Returns:
            List of safety notes
        """
        return []
    
    def to_llm_description(self) -> str:
        """
        Generate a description suitable for LLM prompts.
        
        Returns:
            Formatted description for LLM consumption
        """
        description = f"## {self.name}\n\n"
        description += f"**Description:** {self.description}\n\n"
        
        if self.parameters.get("properties"):
            description += "**Parameters:**\n"
            for param_name, param_info in self.parameters["properties"].items():
                required_marker = " (required)" if param_name in self.parameters.get("required", []) else ""
                description += f"- `{param_name}`: {param_info.get('description', 'No description')}{required_marker}\n"
            description += "\n"
        
        examples = self.get_usage_examples()
        if examples:
            description += "**Example Usage:**\n"
            for i, example in enumerate(examples[:2], 1):  # Limit to 2 examples
                description += f"{i}. {example.get('description', 'Example usage')}\n"
            description += "\n"
        
        safety_notes = self.get_safety_notes()
        if safety_notes:
            description += "**Safety Notes:**\n"
            for note in safety_notes:
                description += f"- {note}\n"
            description += "\n"
        
        return description