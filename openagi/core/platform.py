"""Main OpenAGI platform implementation."""

import asyncio
import signal
import sys
from typing import Any, Dict, List, Optional, Type

from openagi.core.config import OpenAGIConfig
from openagi.core.logger import OpenAGILogger, configure_logging_from_config, get_openagi_logger
from openagi.debugging.engine import DebugEngine
from openagi.monitoring.system import MonitoringSystem
from openagi.api.server import APIServer


class OpenAGIPlatform:
    """Main OpenAGI platform that orchestrates all components."""
    
    def __init__(self, config: Optional[OpenAGIConfig] = None):
        """Initialize the OpenAGI platform."""
        self.config = config or OpenAGIConfig()
        
        # Configure logging first
        configure_logging_from_config(self.config)
        self.logger = get_openagi_logger("platform")
        
        # Initialize components
        self.debug_engine: Optional[DebugEngine] = None
        self.monitoring_system: Optional[MonitoringSystem] = None
        self.api_server: Optional[APIServer] = None
        
        # Runtime state
        self._running = False
        self._tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        
        self.logger.info("OpenAGI platform initialized", version=self.config.app_version)
    
    async def initialize(self) -> None:
        """Initialize all platform components."""
        self.logger.info("Initializing OpenAGI platform components")
        
        try:
            # Initialize debugging engine
            if self.config.debugging.enable_auto_debug:
                self.debug_engine = DebugEngine(self.config)
                await self.debug_engine.initialize()
                self.logger.info("Debug engine initialized")
            
            # Initialize monitoring system
            if self.config.monitoring.enable_metrics:
                self.monitoring_system = MonitoringSystem(self.config)
                await self.monitoring_system.initialize()
                self.logger.info("Monitoring system initialized")
            
            # Initialize API server
            self.api_server = APIServer(self.config, self)
            await self.api_server.initialize()
            self.logger.info("API server initialized")
            
            self.logger.info("All platform components initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize platform", error=str(e))
            await self.shutdown()
            raise
    
    async def start(self) -> None:
        """Start the OpenAGI platform."""
        if self._running:
            self.logger.warning("Platform is already running")
            return
        
        self.logger.info("Starting OpenAGI platform")
        self._running = True
        
        try:
            # Start all components
            if self.debug_engine:
                task = asyncio.create_task(self.debug_engine.start())
                self._tasks.append(task)
            
            if self.monitoring_system:
                task = asyncio.create_task(self.monitoring_system.start())
                self._tasks.append(task)
            
            if self.api_server:
                task = asyncio.create_task(self.api_server.start())
                self._tasks.append(task)
            
            # Start health monitoring
            task = asyncio.create_task(self._health_monitor())
            self._tasks.append(task)
            
            self.logger.info("OpenAGI platform started successfully")
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
        except Exception as e:
            self.logger.error("Failed to start platform", error=str(e))
            await self.shutdown()
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the OpenAGI platform gracefully."""
        if not self._running:
            return
        
        self.logger.info("Shutting down OpenAGI platform")
        self._running = False
        self._shutdown_event.set()
        
        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Shutdown components
        if self.api_server:
            await self.api_server.shutdown()
        
        if self.monitoring_system:
            await self.monitoring_system.shutdown()
        
        if self.debug_engine:
            await self.debug_engine.shutdown()
        
        self.logger.info("OpenAGI platform shutdown complete")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        if sys.platform != "win32":
            loop = asyncio.get_event_loop()
            
            def signal_handler(signum: int) -> None:
                self.logger.info(f"Received signal {signum}, initiating shutdown")
                asyncio.create_task(self.shutdown())
            
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, signal_handler, sig)
    
    async def _health_monitor(self) -> None:
        """Monitor platform health and trigger self-debugging if needed."""
        while self._running:
            try:
                await asyncio.sleep(self.config.debugging.health_check_interval)
                
                # Perform health checks
                health_status = await self._check_health()
                
                if not health_status["healthy"]:
                    self.logger.warning("Health check failed", status=health_status)
                    
                    # Trigger self-debugging if enabled
                    if self.debug_engine and self.config.debugging.enable_self_healing:
                        await self.debug_engine.trigger_self_healing(health_status)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Health monitor error", error=str(e))
    
    async def _check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "healthy": True,
            "components": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Check component health
        if self.debug_engine:
            try:
                engine_health = await self.debug_engine.health_check()
                health_status["components"]["debug_engine"] = engine_health
                if not engine_health.get("healthy", False):
                    health_status["healthy"] = False
            except Exception as e:
                health_status["components"]["debug_engine"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
        
        if self.monitoring_system:
            try:
                monitoring_health = await self.monitoring_system.health_check()
                health_status["components"]["monitoring_system"] = monitoring_health
                if not monitoring_health.get("healthy", False):
                    health_status["healthy"] = False
            except Exception as e:
                health_status["components"]["monitoring_system"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
        
        if self.api_server:
            try:
                api_health = await self.api_server.health_check()
                health_status["components"]["api_server"] = api_health
                if not api_health.get("healthy", False):
                    health_status["healthy"] = False
            except Exception as e:
                health_status["components"]["api_server"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
        
        return health_status
    
    async def run(self) -> None:
        """Run the platform (initialize, start, and wait for shutdown)."""
        try:
            await self.initialize()
            await self.start()
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            self.logger.error("Platform runtime error", error=str(e))
        finally:
            await self.shutdown()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current platform status."""
        return {
            "running": self._running,
            "config": {
                "app_name": self.config.app_name,
                "version": self.config.app_version,
                "environment": self.config.environment,
            },
            "components": {
                "debug_engine": self.debug_engine is not None,
                "monitoring_system": self.monitoring_system is not None,
                "api_server": self.api_server is not None,
            },
            "tasks": len(self._tasks)
        }


async def main() -> None:
    """Main entry point for OpenAGI platform."""
    platform = OpenAGIPlatform()
    await platform.run()


if __name__ == "__main__":
    asyncio.run(main())