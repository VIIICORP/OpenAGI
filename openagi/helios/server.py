"""
Helios WebSocket Server

Provides real-time communication between the agent and the visualization dashboard.
"""

import asyncio
import json
import logging
import threading
from typing import Set, Dict, Any, Optional
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class HeliosServer:
    """
    WebSocket server for real-time agent visualization.
    
    Broadcasts agent state changes, thoughts, and actions to connected
    web clients for live monitoring of the agent's consciousness.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the Helios server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self.running = False
        self.server_thread = None
        
        # Latest agent state for new connections
        self.latest_state = {
            "state": "DISCONNECTED",
            "timestamp": None,
            "message": "Agent not connected"
        }
    
    def start(self):
        """Start the Helios server in a background thread."""
        if self.running:
            logger.warning("Helios server is already running")
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        logger.info(f"🌟 Helios server starting at ws://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the Helios server."""
        if not self.running:
            return
        
        self.running = False
        logger.info("⭐ Helios server stopping")
    
    def _run_server(self):
        """Run the WebSocket server in an asyncio event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._start_websocket_server())
        except Exception as e:
            logger.error(f"Helios server error: {e}")
        finally:
            loop.close()
    
    async def _start_websocket_server(self):
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port
            )
            
            logger.info(f"✨ Helios server started at ws://{self.host}:{self.port}")
            
            # Keep the server running
            while self.running:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Failed to start Helios server: {e}")
        finally:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a new client connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        logger.info(f"🔗 New Helios client connected from {websocket.remote_address}")
        
        # Add client to set
        self.clients.add(websocket)
        
        # Send latest state to new client
        await self._send_to_client(websocket, {
            "type": "state_update",
            "data": self.latest_state
        })
        
        try:
            # Listen for client messages (if any)
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Helios client disconnected")
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            # Remove client from set
            self.clients.discard(websocket)
    
    async def _handle_client_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """
        Handle a message from a client.
        
        Args:
            websocket: Client websocket
            data: Message data
        """
        message_type = data.get("type")
        
        if message_type == "ping":
            await self._send_to_client(websocket, {"type": "pong"})
        elif message_type == "request_status":
            await self._send_to_client(websocket, {
                "type": "status",
                "data": self.latest_state
            })
        else:
            logger.debug(f"Unknown message type from client: {message_type}")
    
    async def _send_to_client(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """
        Send data to a specific client.
        
        Args:
            websocket: Client websocket
            data: Data to send
        """
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
    
    def broadcast(self, data: Dict[str, Any]):
        """
        Broadcast data to all connected clients.
        
        Args:
            data: Data to broadcast
        """
        if not self.clients:
            return
        
        # Update latest state if this is a state update
        if data.get("type") == "state_update":
            self.latest_state = data.get("data", self.latest_state)
        
        # Create async task to send to all clients
        if self.running:
            asyncio.create_task(self._broadcast_async(data))
    
    async def _broadcast_async(self, data: Dict[str, Any]):
        """
        Async broadcast to all clients.
        
        Args:
            data: Data to broadcast
        """
        if not self.clients:
            return
        
        # Send to all clients
        disconnected_clients = set()
        
        for client in self.clients.copy():
            try:
                await self._send_to_client(client, data)
            except Exception as e:
                logger.warning(f"Failed to send to client, removing: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics.
        
        Returns:
            Dictionary containing server stats
        """
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port,
            "connected_clients": len(self.clients),
            "latest_state": self.latest_state
        }

# Global server instance
helios_server = HeliosServer()