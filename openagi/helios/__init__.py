"""
Helios - Real-time visualization dashboard server for OpenAGI.

This module provides a WebSocket-based server for real-time monitoring
and visualization of the agent's state, tasks, and performance.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Set, Optional
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets library not available. Helios dashboard will be disabled.")

class HeliosServer:
    """
    Real-time visualization server for OpenAGI.
    
    Provides a WebSocket server that broadcasts agent state, metrics,
    and events to connected web clients for live monitoring.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the Helios server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.is_running = False
        self.server = None
        
        # Connected clients
        self.clients: Set[WebSocketServerProtocol] = set()
        
        # Agent reference (will be set externally)
        self.agent_engine = None
        self.memory_manager = None
        self.model_manager = None
        self.voice_interface = None
        
        # Dashboard state
        self.dashboard_data = {
            "agent_status": {},
            "memory_stats": {},
            "model_info": {},
            "voice_status": {},
            "recent_events": [],
            "performance_metrics": {},
            "system_info": {}
        }
        
        # Update interval
        self.update_interval = 1.0  # seconds
        self.last_update = time.time()
        
    async def start_server(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("Cannot start Helios server - websockets library not available")
            return False
        
        if self.is_running:
            logger.warning("Helios server is already running")
            return True
        
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            
            self.is_running = True
            logger.info(f"Helios dashboard server started on ws://{self.host}:{self.port}")
            
            # Start the dashboard update loop
            asyncio.create_task(self.update_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Helios server: {e}")
            return False
    
    async def stop_server(self):
        """Stop the WebSocket server."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Disconnect all clients
        if self.clients:
            await asyncio.gather(
                *[client.close() for client in self.clients],
                return_exceptions=True
            )
            self.clients.clear()
        
        logger.info("Helios dashboard server stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new client connection."""
        client_address = websocket.remote_address
        logger.info(f"New client connected: {client_address}")
        
        self.clients.add(websocket)
        
        try:
            # Send initial dashboard state
            await self.send_to_client(websocket, {
                "type": "initial_state",
                "data": self.dashboard_data
            })
            
            # Listen for client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {client_address}: {message}")
                except Exception as e:
                    logger.error(f"Error handling message from {client_address}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_address}")
        except Exception as e:
            logger.error(f"Error with client {client_address}: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle a message from a client."""
        message_type = data.get("type")
        
        if message_type == "ping":
            await self.send_to_client(websocket, {
                "type": "pong",
                "timestamp": time.time()
            })
        
        elif message_type == "request_update":
            # Send current dashboard state
            await self.send_to_client(websocket, {
                "type": "dashboard_update",
                "data": self.dashboard_data
            })
        
        elif message_type == "agent_command":
            # Handle agent control commands
            await self.handle_agent_command(websocket, data.get("command", {}))
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def handle_agent_command(self, websocket: WebSocketServerProtocol, command: Dict):
        """Handle agent control commands from the dashboard."""
        command_type = command.get("type")
        
        try:
            if command_type == "set_goal" and self.agent_engine:
                goal = command.get("goal", "")
                self.agent_engine.set_goal(goal)
                
                await self.send_to_client(websocket, {
                    "type": "command_result",
                    "success": True,
                    "message": f"Goal set: {goal}"
                })
            
            elif command_type == "add_task" and self.agent_engine:
                task = command.get("task", "")
                self.agent_engine.add_task(task)
                
                await self.send_to_client(websocket, {
                    "type": "command_result",
                    "success": True,
                    "message": f"Task added: {task}"
                })
            
            elif command_type == "pause_agent" and self.agent_engine:
                self.agent_engine.pause()
                
                await self.send_to_client(websocket, {
                    "type": "command_result",
                    "success": True,
                    "message": "Agent paused"
                })
            
            elif command_type == "resume_agent" and self.agent_engine:
                self.agent_engine.resume()
                
                await self.send_to_client(websocket, {
                    "type": "command_result",
                    "success": True,
                    "message": "Agent resumed"
                })
            
            else:
                await self.send_to_client(websocket, {
                    "type": "command_result",
                    "success": False,
                    "message": f"Unknown or unavailable command: {command_type}"
                })
                
        except Exception as e:
            logger.error(f"Error executing command {command_type}: {e}")
            await self.send_to_client(websocket, {
                "type": "command_result",
                "success": False,
                "message": f"Command failed: {str(e)}"
            })
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, data: Dict):
        """Send data to a specific client."""
        try:
            message = json.dumps(data)
            await websocket.send(message)
        except Exception as e:
            logger.error(f"Failed to send message to client: {e}")
    
    async def broadcast_to_all(self, data: Dict):
        """Broadcast data to all connected clients."""
        if not self.clients:
            return
        
        message = json.dumps(data)
        
        # Send to all clients
        await asyncio.gather(
            *[self.send_to_client(client, data) for client in self.clients.copy()],
            return_exceptions=True
        )
    
    async def update_loop(self):
        """Main update loop for dashboard data."""
        while self.is_running:
            try:
                await self.update_dashboard_data()
                
                # Broadcast update if we have clients
                if self.clients:
                    await self.broadcast_to_all({
                        "type": "dashboard_update",
                        "data": self.dashboard_data
                    })
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(1.0)  # Brief pause on error
    
    async def update_dashboard_data(self):
        """Update the dashboard data from connected components."""
        current_time = time.time()
        
        # Update agent status
        if self.agent_engine:
            self.dashboard_data["agent_status"] = self.agent_engine.get_status()
        
        # Update memory stats
        if self.memory_manager:
            self.dashboard_data["memory_stats"] = self.memory_manager.get_memory_stats()
        
        # Update model info
        if self.model_manager:
            self.dashboard_data["model_info"] = self.model_manager.get_status()
        
        # Update voice status
        if self.voice_interface:
            self.dashboard_data["voice_status"] = self.voice_interface.get_status()
        
        # Update performance metrics
        self.dashboard_data["performance_metrics"] = {
            "uptime": current_time - self.last_update if hasattr(self, 'start_time') else 0,
            "connected_clients": len(self.clients),
            "last_update": current_time,
            "update_interval": self.update_interval
        }
        
        # Update system info
        self.dashboard_data["system_info"] = self.get_system_info()
        
        self.last_update = current_time
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import psutil
        import platform
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "timestamp": datetime.now().isoformat(),
                "note": "psutil not available for detailed system metrics"
            }
    
    def connect_agent_engine(self, agent_engine):
        """Connect the agent engine for monitoring."""
        self.agent_engine = agent_engine
        
        # Register event callbacks
        agent_engine.register_event_callback('state_change', self.on_agent_state_change)
        agent_engine.register_event_callback('goal_completed', self.on_goal_completed)
        agent_engine.register_event_callback('cycle_completed', self.on_cycle_completed)
        agent_engine.register_event_callback('error_occurred', self.on_error_occurred)
        
        logger.info("Agent engine connected to Helios dashboard")
    
    def connect_memory_manager(self, memory_manager):
        """Connect the memory manager for monitoring."""
        self.memory_manager = memory_manager
        logger.info("Memory manager connected to Helios dashboard")
    
    def connect_model_manager(self, model_manager):
        """Connect the model manager for monitoring."""
        self.model_manager = model_manager
        logger.info("Model manager connected to Helios dashboard")
    
    def connect_voice_interface(self, voice_interface):
        """Connect the voice interface for monitoring."""
        self.voice_interface = voice_interface
        logger.info("Voice interface connected to Helios dashboard")
    
    def on_agent_state_change(self, data: Dict):
        """Handle agent state change events."""
        event = {
            "type": "agent_state_change",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.add_event(event)
    
    def on_goal_completed(self, data: Dict):
        """Handle goal completion events."""
        event = {
            "type": "goal_completed",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.add_event(event)
    
    def on_cycle_completed(self, data: Dict):
        """Handle cycle completion events."""
        event = {
            "type": "cycle_completed",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.add_event(event)
    
    def on_error_occurred(self, data: Dict):
        """Handle error events."""
        event = {
            "type": "error_occurred",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.add_event(event)
    
    def add_event(self, event: Dict):
        """Add an event to the recent events list."""
        self.dashboard_data["recent_events"].append(event)
        
        # Keep only the last 100 events
        if len(self.dashboard_data["recent_events"]) > 100:
            self.dashboard_data["recent_events"] = self.dashboard_data["recent_events"][-100:]
        
        # Broadcast event immediately if we have clients
        if self.clients and self.is_running:
            asyncio.create_task(self.broadcast_to_all({
                "type": "new_event",
                "event": event
            }))
    
    def get_dashboard_url(self) -> str:
        """Get the dashboard WebSocket URL."""
        return f"ws://{self.host}:{self.port}"
    
    def is_server_running(self) -> bool:
        """Check if the server is running."""
        return self.is_running and WEBSOCKETS_AVAILABLE