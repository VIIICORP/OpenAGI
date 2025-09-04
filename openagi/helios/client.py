"""
Helios Client - Interface for the agent to send status updates to the visualization dashboard.
"""
from typing import Dict, Any
from .server import helios_server

class HeliosClient:
    """
    A client that allows the agent to send status updates to the Helios server.
    This provides the light that illuminates the agent's consciousness.
    """
    
    def __init__(self):
        """Initialize the Helios client."""
        self.server = helios_server
        self.enabled = True
    
    def send_status_update(self, status_data: Dict[str, Any]) -> None:
        """
        Send a status update to the Helios dashboard.
        
        Args:
            status_data: Status information to broadcast
        """
        if not self.enabled:
            return
        
        message = {
            "type": "agent_status",
            "timestamp": status_data.get("timestamp"),
            "data": status_data
        }
        
        self.server.send_message(message)
    
    def send_goal_update(self, goal: str, status: str) -> None:
        """
        Send a goal-related update.
        
        Args:
            goal: The goal being processed
            status: Current status of the goal
        """
        if not self.enabled:
            return
        
        message = {
            "type": "goal_update",
            "goal": goal,
            "status": status,
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def send_plan_update(self, plan: Dict[str, Any]) -> None:
        """
        Send a plan update.
        
        Args:
            plan: The generated plan
        """
        if not self.enabled:
            return
        
        message = {
            "type": "plan_update",
            "plan": plan,
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def send_execution_update(self, step: int, tool: str, result: Dict[str, Any]) -> None:
        """
        Send an execution step update.
        
        Args:
            step: Step number
            tool: Tool being executed
            result: Execution result
        """
        if not self.enabled:
            return
        
        message = {
            "type": "execution_update",
            "step": step,
            "tool": tool,
            "result": result,
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def send_memory_update(self, memory_type: str, operation: str, details: Dict[str, Any]) -> None:
        """
        Send a memory operation update.
        
        Args:
            memory_type: Type of memory (short_term, long_term)
            operation: Operation performed (store, recall, etc.)
            details: Operation details
        """
        if not self.enabled:
            return
        
        message = {
            "type": "memory_update",
            "memory_type": memory_type,
            "operation": operation,
            "details": details,
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def send_error(self, error: str, context: Dict[str, Any] = None) -> None:
        """
        Send an error notification.
        
        Args:
            error: Error message
            context: Additional context about the error
        """
        if not self.enabled:
            return
        
        message = {
            "type": "error",
            "error": error,
            "context": context or {},
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def send_custom_message(self, message_type: str, data: Dict[str, Any]) -> None:
        """
        Send a custom message.
        
        Args:
            message_type: Type of the message
            data: Message data
        """
        if not self.enabled:
            return
        
        message = {
            "type": message_type,
            "data": data,
            "timestamp": self.get_timestamp()
        }
        
        self.server.send_message(message)
    
    def get_timestamp(self) -> float:
        """Get the current timestamp."""
        import time
        return time.time()
    
    def enable(self) -> None:
        """Enable the Helios client."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the Helios client."""
        self.enabled = False

# Global client instance
helios_client = HeliosClient()