"""
Helios Server - Real-time WebSocket server for agent visualization.
"""
import asyncio
import json
import threading
from typing import Set, Dict, Any, Optional

# Import websockets conditionally
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

class HeliosServer:
    """
    WebSocket server that broadcasts the agent's status in real-time.
    This is the beacon that shines light on the agent's inner workings.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the Helios server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        self.running = False
        
        if WEBSOCKETS_AVAILABLE:
            # Message queue for broadcasting
            self.message_queue = asyncio.Queue()
            print(f"INFO: [Helios] Server initialized at ws://{host}:{port}")
        else:
            print(f"WARNING: [Helios] WebSockets not available. Helios server disabled.")
    
    async def register_client(self, websocket) -> None:
        """Register a new client connection."""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            "type": "connection",
            "status": "connected",
            "message": "Welcome to Helios - The Light of OpenAGI"
        }))
        print(f"INFO: [Helios] Client connected. Total clients: {len(self.clients)}")
    
    async def unregister_client(self, websocket) -> None:
        """Unregister a client connection."""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        self.clients.discard(websocket)
        print(f"INFO: [Helios] Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        if not WEBSOCKETS_AVAILABLE or not self.clients:
            return
        
        message_json = json.dumps(message)
        
        # Send to all clients, removing any that are disconnected
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_json)
            except:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
    
    async def handle_client(self, websocket, path: str) -> None:
        """Handle a client connection."""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                # Handle incoming messages from clients
                try:
                    data = json.loads(message)
                    print(f"INFO: [Helios] Received message from client: {data}")
                    
                    # Echo back for now (could implement commands later)
                    await websocket.send(json.dumps({
                        "type": "echo",
                        "original": data
                    }))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                    
        except:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def message_broadcaster(self) -> None:
        """Background task to broadcast queued messages."""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        while self.running:
            try:
                # Wait for a message with a timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.broadcast_message(message)
            except asyncio.TimeoutError:
                # No message to broadcast, continue
                pass
            except Exception as e:
                print(f"ERROR: [Helios] Broadcasting error: {e}")
    
    async def start_server(self) -> None:
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            print("WARNING: [Helios] Cannot start server - websockets not available")
            return
            
        self.running = True
        
        # Start the message broadcaster
        broadcaster_task = asyncio.create_task(self.message_broadcaster())
        
        # Start the WebSocket server
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"INFO: [Helios] Server started at ws://{self.host}:{self.port}")
        
        try:
            # Keep the server running
            await self.server.wait_closed()
        finally:
            broadcaster_task.cancel()
            self.running = False
    
    def start_in_thread(self) -> threading.Thread:
        """Start the server in a separate thread."""
        def run_server():
            if not WEBSOCKETS_AVAILABLE:
                print("WARNING: [Helios] Cannot start server thread - websockets not available")
                return
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_server())
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        return thread
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to all clients (thread-safe).
        
        Args:
            message: Message to broadcast
        """
        if not WEBSOCKETS_AVAILABLE or not self.running:
            return
            
        # Put message in queue for broadcasting
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(self.message_queue.put_nowait, message)
        except RuntimeError:
            # No event loop in current thread, skip
            pass
    
    def stop(self) -> None:
        """Stop the server."""
        self.running = False
        if self.server:
            self.server.close()

# Global server instance
helios_server = HeliosServer()