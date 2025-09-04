"""
Base class for all tools that the OpenAGI agent can use.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseTool(ABC):
    """
    Abstract base class for all tools available to the OpenAGI agent.
    Tools allow the agent to interact with its environment and perform actions.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the tool does."""
        pass
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema describing the parameters this tool accepts.
        Override this method to specify tool parameters.
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Parameters for the tool execution
            
        Returns:
            Dict containing the result of the tool execution
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary representation for use in prompts.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate the given parameters against the tool's schema.
        
        Args:
            params: Parameters to validate
            
        Returns:
            bool: True if parameters are valid
        """
        # Basic validation - could be enhanced with jsonschema
        schema = self.parameters
        required = schema.get("required", [])
        
        # Check required parameters
        for req_param in required:
            if req_param not in params:
                return False
        
        return True