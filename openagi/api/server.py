"""FastAPI server for OpenAGI platform."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.engine import OpenAGIEngine
from ..config.settings import Config


# Pydantic models for API
class TaskRequest(BaseModel):
    """Task request model."""
    id: Optional[str] = None
    type: str = Field(..., description="Type of task to execute")
    data: Dict[str, Any] = Field(..., description="Task data")
    requirements: List[str] = Field(default=[], description="Required capabilities")
    priority: int = Field(default=1, ge=1, le=10, description="Task priority (1-10)")
    timeout: Optional[int] = Field(default=None, description="Task timeout in seconds")


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: str


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str
    capabilities: List[str]
    performance_score: float
    success_rate: float
    task_count: int
    is_busy: bool


class EngineStatus(BaseModel):
    """Engine status model."""
    status: str
    uptime_seconds: float
    metrics: Dict[str, Any]
    agents: List[str]
    plugins: List[str]
    learning_status: Dict[str, Any]


class PluginInfo(BaseModel):
    """Plugin information model."""
    name: str
    version: str
    description: str
    capabilities: List[str]


class LearningRequest(BaseModel):
    """Learning request model."""
    data: Dict[str, Any]
    learning_type: str = "supervised"
    algorithm: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OpenAGIServer:
    """
    FastAPI server for OpenAGI platform.
    
    Provides REST API endpoints for interacting with the AGI system,
    managing agents, executing tasks, and monitoring system status.
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = logging.getLogger("openagi.server")
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="OpenAGI Platform",
            description="Comprehensive AI Platform with 30M+ Self-Learning Features",
            version="0.1.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS
        if self.config.get("api.cors_enabled", True):
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # In production, specify allowed origins
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Initialize OpenAGI engine
        self.engine: Optional[OpenAGIEngine] = None
        
        # Task queue for background processing
        self.task_queue: List[Dict[str, Any]] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("OpenAGI Server initialized")
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize the engine on startup."""
            await self.initialize_engine()
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown."""
            await self.shutdown_engine()
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {
                "message": "Welcome to OpenAGI Platform",
                "version": "0.1.0",
                "docs": "/docs",
                "status": "/status"
            }
        
        @self.app.get("/status", response_model=EngineStatus)
        async def get_status():
            """Get system status."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            status = self.engine.get_status()
            return EngineStatus(**status)
        
        @self.app.post("/tasks", response_model=TaskResponse)
        async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
            """Create and execute a new task."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            # Generate task ID if not provided
            task_id = task.id or f"task_{datetime.now().timestamp()}"
            
            # Prepare task data
            task_data = {
                "id": task_id,
                "type": task.type,
                "data": task.data,
                "requirements": task.requirements,
                "priority": task.priority,
                "timeout": task.timeout,
                "created_at": datetime.now().isoformat()
            }
            
            # Execute task in background
            background_tasks.add_task(self._execute_task_background, task_data)
            
            # Add to active tasks
            self.active_tasks[task_id] = {
                "status": "queued",
                "task_data": task_data,
                "created_at": datetime.now()
            }
            
            return TaskResponse(
                task_id=task_id,
                status="queued",
                timestamp=datetime.now().isoformat()
            )
        
        @self.app.get("/tasks/{task_id}", response_model=TaskResponse)
        async def get_task(task_id: str):
            """Get task status and results."""
            if task_id not in self.active_tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task_info = self.active_tasks[task_id]
            
            return TaskResponse(
                task_id=task_id,
                status=task_info["status"],
                result=task_info.get("result"),
                error=task_info.get("error"),
                agent=task_info.get("agent"),
                execution_time=task_info.get("execution_time"),
                timestamp=task_info.get("timestamp", datetime.now().isoformat())
            )
        
        @self.app.get("/tasks", response_model=List[TaskResponse])
        async def list_tasks():
            """List all tasks."""
            tasks = []
            for task_id, task_info in self.active_tasks.items():
                tasks.append(TaskResponse(
                    task_id=task_id,
                    status=task_info["status"],
                    result=task_info.get("result"),
                    error=task_info.get("error"),
                    agent=task_info.get("agent"),
                    execution_time=task_info.get("execution_time"),
                    timestamp=task_info.get("timestamp", datetime.now().isoformat())
                ))
            return tasks
        
        @self.app.get("/agents", response_model=List[AgentInfo])
        async def list_agents():
            """List all agents."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            agents = []
            for agent_name, agent in self.engine.agents.items():
                agents.append(AgentInfo(
                    name=agent.name,
                    capabilities=list(agent.capabilities),
                    performance_score=agent.performance_score,
                    success_rate=agent.success_rate,
                    task_count=len(agent.task_history),
                    is_busy=agent.is_busy
                ))
            return agents
        
        @self.app.get("/agents/{agent_name}", response_model=AgentInfo)
        async def get_agent(agent_name: str):
            """Get specific agent information."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            if agent_name not in self.engine.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent = self.engine.agents[agent_name]
            return AgentInfo(
                name=agent.name,
                capabilities=list(agent.capabilities),
                performance_score=agent.performance_score,
                success_rate=agent.success_rate,
                task_count=len(agent.task_history),
                is_busy=agent.is_busy
            )
        
        @self.app.get("/plugins", response_model=List[PluginInfo])
        async def list_plugins():
            """List all available plugins."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            plugins = []
            for plugin_name, plugin in self.engine.plugin_manager.plugins.items():
                plugins.append(PluginInfo(
                    name=plugin.name,
                    version=plugin.version,
                    description=plugin.description,
                    capabilities=plugin.capabilities
                ))
            return plugins
        
        @self.app.get("/plugins/stats", response_model=Dict[str, Any])
        async def get_plugin_stats():
            """Get plugin statistics."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            return self.engine.plugin_manager.get_plugin_stats()
        
        @self.app.post("/learn", response_model=Dict[str, Any])
        async def learn(learning_request: LearningRequest):
            """Trigger learning from provided data."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            try:
                # Create a learning task
                learning_task = {
                    "id": f"learning_{datetime.now().timestamp()}",
                    "type": "learning_task",
                    "data": {
                        "training_data": learning_request.data,
                        "learning_type": learning_request.learning_type,
                        "algorithm": learning_request.algorithm,
                        "parameters": learning_request.parameters
                    }
                }
                
                # Execute learning task
                result = await self.engine.process_task(learning_task)
                
                return {
                    "status": "success",
                    "learning_result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Learning failed: {str(e)}")
        
        @self.app.post("/evolve", response_model=Dict[str, Any])
        async def evolve():
            """Trigger system evolution."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            try:
                await self.engine.evolve()
                
                return {
                    "status": "success",
                    "message": "Evolution cycle completed",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")
        
        @self.app.get("/learning/status", response_model=Dict[str, Any])
        async def get_learning_status():
            """Get learning system status."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            return self.engine.learning_system.get_status()
        
        @self.app.get("/metrics", response_model=Dict[str, Any])
        async def get_metrics():
            """Get system metrics."""
            if not self.engine:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            
            return {
                "engine_metrics": self.engine.metrics,
                "learning_metrics": self.engine.learning_system.get_status(),
                "plugin_metrics": self.engine.plugin_manager.get_plugin_stats(),
                "api_metrics": {
                    "active_tasks": len(self.active_tasks),
                    "queued_tasks": len(self.task_queue)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/config", response_model=Dict[str, Any])
        async def update_config(config_updates: Dict[str, Any]):
            """Update configuration."""
            try:
                for key, value in config_updates.items():
                    self.config.set(key, value)
                
                return {
                    "status": "success",
                    "message": "Configuration updated",
                    "updated_keys": list(config_updates.keys()),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")
        
        @self.app.get("/config", response_model=Dict[str, Any])
        async def get_config():
            """Get current configuration."""
            return self.config.to_dict()
        
        @self.app.get("/health", response_model=Dict[str, Any])
        async def health_check():
            """Health check endpoint."""
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "engine_initialized": self.engine is not None,
                "active_tasks": len(self.active_tasks),
                "system_load": "normal"  # Could add actual system metrics
            }
            
            if self.engine:
                engine_status = self.engine.get_status()
                health_status.update({
                    "agents_count": len(engine_status["agents"]),
                    "plugins_count": len(engine_status["plugins"]),
                    "uptime": engine_status["uptime_seconds"]
                })
            
            return health_status
    
    async def initialize_engine(self) -> None:
        """Initialize the OpenAGI engine."""
        try:
            self.engine = OpenAGIEngine(config_path=None)
            await self.engine.initialize()
            self.logger.info("OpenAGI Engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize engine: {e}")
            raise
    
    async def shutdown_engine(self) -> None:
        """Shutdown the OpenAGI engine."""
        if self.engine:
            try:
                await self.engine.shutdown()
                self.logger.info("OpenAGI Engine shutdown successfully")
            except Exception as e:
                self.logger.error(f"Error during engine shutdown: {e}")
    
    async def _execute_task_background(self, task_data: Dict[str, Any]) -> None:
        """Execute task in background."""
        task_id = task_data["id"]
        
        try:
            # Update status to processing
            self.active_tasks[task_id]["status"] = "processing"
            self.active_tasks[task_id]["started_at"] = datetime.now()
            
            # Execute task
            result = await self.engine.process_task(task_data)
            
            # Update task with results
            self.active_tasks[task_id].update({
                "status": result["status"],
                "result": result.get("result"),
                "error": result.get("error"),
                "agent": result.get("agent"),
                "execution_time": result.get("execution_time"),
                "timestamp": result.get("timestamp"),
                "completed_at": datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"Task {task_id} execution failed: {e}")
            self.active_tasks[task_id].update({
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "completed_at": datetime.now()
            })
    
    def run(self, host: str = None, port: int = None, **kwargs) -> None:
        """Run the server."""
        host = host or self.config.get("api.host", "0.0.0.0")
        port = port or self.config.get("api.port", 8000)
        
        self.logger.info(f"Starting OpenAGI Server on {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=self.config.get("logging.level", "info").lower(),
            **kwargs
        )


# Convenience function to create and run server
def create_server(config: Config = None) -> OpenAGIServer:
    """Create OpenAGI server instance."""
    return OpenAGIServer(config)


def run_server(config_path: str = None, host: str = None, port: int = None) -> None:
    """Run OpenAGI server."""
    config = Config(config_path) if config_path else Config()
    server = create_server(config)
    server.run(host=host, port=port)