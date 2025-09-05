"""
FastAPI server for OpenAGI platform.

Provides RESTful API endpoints for:
- Platform status and health checks
- Debugging and monitoring information
- AI model management
- Configuration management
- Real-time metrics and alerts
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from openagi.core.config import OpenAGIConfig
from openagi.core.logger import get_openagi_logger


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    components: Dict[str, Any]


class MetricsResponse(BaseModel):
    """Metrics response model."""
    timestamp: datetime
    metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    performance_analysis: Dict[str, Any]


class DebugEventResponse(BaseModel):
    """Debug event response model."""
    event_id: int
    timestamp: datetime
    event_type: str
    severity: str
    component: str
    message: str
    resolved: bool
    resolution_strategy: Optional[str]


class PlatformStatusResponse(BaseModel):
    """Platform status response model."""
    running: bool
    config: Dict[str, Any]
    components: Dict[str, bool]
    tasks: int
    uptime_seconds: float


class APIServer:
    """FastAPI server for OpenAGI platform."""
    
    def __init__(self, config: OpenAGIConfig, platform):
        self.config = config
        self.platform = platform
        self.logger = get_openagi_logger("api_server")
        
        # FastAPI app
        self.app = FastAPI(
            title="OpenAGI Platform API",
            description="Comprehensive AI Platform with Self-Debugging Features",
            version=config.app_version,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Server state
        self._server = None
        self._start_time = time.time()
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request, call_next):
            start_time = time.time()
            
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            # Record metrics if monitoring is available
            if (self.platform.monitoring_system and 
                hasattr(self.platform.monitoring_system, 'metrics_collector')):
                self.platform.monitoring_system.metrics_collector.record_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    duration=duration
                )
            
            self.logger.info(
                "HTTP request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {
                "message": "OpenAGI Platform API",
                "version": self.config.app_version,
                "docs": "/docs"
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health():
            """Health check endpoint."""
            try:
                # Get component health
                components = {}
                
                if self.platform.debug_engine:
                    components["debug_engine"] = await self.platform.debug_engine.health_check()
                
                if self.platform.monitoring_system:
                    components["monitoring_system"] = await self.platform.monitoring_system.health_check()
                
                # Determine overall status
                all_healthy = all(
                    comp.get("healthy", False) for comp in components.values()
                )
                status = "healthy" if all_healthy else "degraded"
                
                return HealthResponse(
                    status=status,
                    timestamp=datetime.now(),
                    version=self.config.app_version,
                    uptime_seconds=time.time() - self._start_time,
                    components=components
                )
                
            except Exception as e:
                self.logger.error("Health check failed", error=str(e))
                raise HTTPException(status_code=500, detail="Health check failed")
        
        @self.app.get("/status", response_model=PlatformStatusResponse)
        async def status():
            """Platform status endpoint."""
            try:
                platform_status = self.platform.get_status()
                platform_status["uptime_seconds"] = time.time() - self._start_time
                
                return PlatformStatusResponse(**platform_status)
                
            except Exception as e:
                self.logger.error("Status check failed", error=str(e))
                raise HTTPException(status_code=500, detail="Status check failed")
        
        @self.app.get("/metrics", response_model=MetricsResponse)
        async def metrics():
            """Get current metrics."""
            try:
                if not self.platform.monitoring_system:
                    raise HTTPException(status_code=503, detail="Monitoring system not available")
                
                monitoring_data = self.platform.monitoring_system.monitoring_data
                
                return MetricsResponse(
                    timestamp=monitoring_data.get("timestamp", datetime.now()),
                    metrics=monitoring_data.get("metrics", {}),
                    alerts=monitoring_data.get("alerts", []),
                    performance_analysis=monitoring_data.get("performance_analysis", {})
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Metrics retrieval failed", error=str(e))
                raise HTTPException(status_code=500, detail="Metrics retrieval failed")
        
        @self.app.get("/metrics/summary")
        async def metrics_summary():
            """Get metrics summary."""
            try:
                if not self.platform.monitoring_system:
                    raise HTTPException(status_code=503, detail="Monitoring system not available")
                
                return self.platform.monitoring_system.get_metrics_summary()
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Metrics summary failed", error=str(e))
                raise HTTPException(status_code=500, detail="Metrics summary failed")
        
        @self.app.get("/alerts")
        async def alerts():
            """Get current alerts."""
            try:
                if not self.platform.monitoring_system:
                    raise HTTPException(status_code=503, detail="Monitoring system not available")
                
                return self.platform.monitoring_system.get_alerts_summary()
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Alerts retrieval failed", error=str(e))
                raise HTTPException(status_code=500, detail="Alerts retrieval failed")
        
        @self.app.get("/debug/events", response_model=List[DebugEventResponse])
        async def debug_events(limit: int = 100):
            """Get recent debug events."""
            try:
                if not self.platform.debug_engine:
                    raise HTTPException(status_code=503, detail="Debug engine not available")
                
                events = []
                for event in self.platform.debug_engine.debug_history[-limit:]:
                    events.append(DebugEventResponse(
                        event_id=id(event),
                        timestamp=event.timestamp,
                        event_type=event.event_type,
                        severity=event.severity,
                        component=event.component,
                        message=event.message,
                        resolved=event.resolved,
                        resolution_strategy=event.resolution_strategy
                    ))
                
                return events
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Debug events retrieval failed", error=str(e))
                raise HTTPException(status_code=500, detail="Debug events retrieval failed")
        
        @self.app.get("/debug/stats")
        async def debug_stats():
            """Get debug engine statistics."""
            try:
                if not self.platform.debug_engine:
                    raise HTTPException(status_code=503, detail="Debug engine not available")
                
                return {
                    "metrics": self.platform.debug_engine.metrics,
                    "active_issues": len(self.platform.debug_engine.active_issues),
                    "total_history": len(self.platform.debug_engine.debug_history)
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Debug stats retrieval failed", error=str(e))
                raise HTTPException(status_code=500, detail="Debug stats retrieval failed")
        
        @self.app.post("/debug/trigger-healing")
        async def trigger_healing(background_tasks: BackgroundTasks):
            """Manually trigger self-healing process."""
            try:
                if not self.platform.debug_engine:
                    raise HTTPException(status_code=503, detail="Debug engine not available")
                
                # Trigger healing in background
                background_tasks.add_task(self._trigger_healing_task)
                
                return {"message": "Self-healing process triggered"}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error("Healing trigger failed", error=str(e))
                raise HTTPException(status_code=500, detail="Healing trigger failed")
        
        @self.app.get("/config")
        async def config():
            """Get current configuration (sanitized)."""
            try:
                config_dict = self.config.to_dict()
                
                # Remove sensitive information
                sensitive_keys = ["security_key", "password", "secret"]
                for key in list(config_dict.keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        config_dict[key] = "***REDACTED***"
                
                return config_dict
                
            except Exception as e:
                self.logger.error("Config retrieval failed", error=str(e))
                raise HTTPException(status_code=500, detail="Config retrieval failed")
        
        @self.app.post("/shutdown")
        async def shutdown(background_tasks: BackgroundTasks):
            """Gracefully shutdown the platform."""
            try:
                self.logger.info("Shutdown requested via API")
                background_tasks.add_task(self._shutdown_task)
                
                return {"message": "Platform shutdown initiated"}
                
            except Exception as e:
                self.logger.error("Shutdown request failed", error=str(e))
                raise HTTPException(status_code=500, detail="Shutdown request failed")
    
    async def _trigger_healing_task(self) -> None:
        """Background task to trigger healing."""
        try:
            health_status = await self.platform._check_health()
            await self.platform.debug_engine.trigger_self_healing(health_status)
        except Exception as e:
            self.logger.error("Healing task failed", error=str(e))
    
    async def _shutdown_task(self) -> None:
        """Background task to shutdown platform."""
        # Wait a bit to allow response to be sent
        await asyncio.sleep(1)
        await self.platform.shutdown()
    
    async def initialize(self) -> None:
        """Initialize the API server."""
        self.logger.info("Initializing API server")
        self.logger.info("API server initialized")
    
    async def start(self) -> None:
        """Start the API server."""
        self.logger.info(f"Starting API server on {self.config.api.host}:{self.config.api.port}")
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=self.app,
            host=self.config.api.host,
            port=self.config.api.port,
            log_level="info",
            access_log=False,  # We handle logging in middleware
        )
        
        self._server = uvicorn.Server(config)
        
        # Start server
        await self._server.serve()
    
    async def shutdown(self) -> None:
        """Shutdown the API server."""
        self.logger.info("Shutting down API server")
        
        if self._server:
            self._server.should_exit = True
        
        self.logger.info("API server shutdown complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of API server."""
        return {
            "healthy": self._server is not None,
            "uptime_seconds": time.time() - self._start_time,
            "config": {
                "host": self.config.api.host,
                "port": self.config.api.port
            }
        }