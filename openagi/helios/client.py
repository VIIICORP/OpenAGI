"""
Helios Client

Allows the agent to communicate with the Helios visualization server.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from .server import helios_server

logger = logging.getLogger(__name__)

class HeliosClient:
    """
    A client that allows the agent to send status updates to the Helios server.
    
    This provides the communication bridge between the agent's internal state
    and the real-time visualization dashboard.
    """
    
    def __init__(self):
        """Initialize the Helios client."""
        self.server = helios_server
        self.connected = False
    
    def connect(self):
        """Connect to the Helios server."""
        if not self.server.running:
            self.server.start()
        
        self.connected = True
        logger.info("🌟 Connected to Helios visualization server")
        
        # Send initial connection message
        self.send_status_update("CONNECTED", "Agent connected to Helios")
    
    def disconnect(self):
        """Disconnect from the Helios server."""
        if self.connected:
            self.send_status_update("DISCONNECTED", "Agent disconnected from Helios")
            self.connected = False
            logger.info("⭐ Disconnected from Helios server")
    
    def send_status_update(self, state: str, message: str = "", context: Dict[str, Any] = None):
        """
        Send a status update to the visualization dashboard.
        
        Args:
            state: Current agent state
            message: Status message
            context: Additional context information
        """
        if not self.connected:
            return
        
        update_data = {
            "state": state,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        self.server.broadcast({
            "type": "state_update",
            "data": update_data
        })
        
        logger.debug(f"Sent status update: {state} - {message}")
    
    def send_thought(self, thought: str, thought_type: str = "general"):
        """
        Send a thought or reasoning process to the dashboard.
        
        Args:
            thought: The thought content
            thought_type: Type of thought (planning, reflection, etc.)
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "thought",
            "data": {
                "content": thought,
                "thought_type": thought_type,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def send_goal_update(self, goal: str, status: str, progress: float = 0.0):
        """
        Send an update about goal progress.
        
        Args:
            goal: The goal being worked on
            status: Current status
            progress: Progress percentage (0.0 to 1.0)
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "goal_update",
            "data": {
                "goal": goal,
                "status": status,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def send_tool_execution(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """
        Send information about tool execution.
        
        Args:
            tool_name: Name of the tool executed
            parameters: Parameters passed to the tool
            result: Result of the tool execution
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "tool_execution",
            "data": {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def send_memory_update(self, memory_type: str, operation: str, content: str):
        """
        Send information about memory operations.
        
        Args:
            memory_type: Type of memory (short_term, long_term, etc.)
            operation: Operation performed (store, recall, etc.)
            content: Brief description of the content
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "memory_update",
            "data": {
                "memory_type": memory_type,
                "operation": operation,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def send_metrics(self, metrics: Dict[str, Any]):
        """
        Send performance metrics to the dashboard.
        
        Args:
            metrics: Dictionary of metrics
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "metrics",
            "data": {
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def send_error(self, error_message: str, error_type: str = "general", context: Dict[str, Any] = None):
        """
        Send error information to the dashboard.
        
        Args:
            error_message: Error message
            error_type: Type of error
            context: Additional error context
        """
        if not self.connected:
            return
        
        self.server.broadcast({
            "type": "error",
            "data": {
                "message": error_message,
                "error_type": error_type,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def is_connected(self) -> bool:
        """
        Check if connected to the Helios server.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected and self.server.running