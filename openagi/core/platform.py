"""
Core OpenAGI Platform Implementation

The main platform class that orchestrates all AI components,
testing frameworks, and system management.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import structlog

from ..config.manager import ConfigManager
from ..models.registry import ModelRegistry
from ..testing.framework import SelfTestSuite
from ..monitoring.metrics import MetricsCollector
from ..database.manager import DatabaseManager
from ..security.auth import AuthenticationManager

logger = structlog.get_logger(__name__)


@dataclass
class PlatformStatus:
    """Platform status information."""
    id: str
    status: str
    uptime: datetime
    models_loaded: int
    tests_running: int
    active_sessions: int
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None


class OpenAGI:
    """
    Main OpenAGI Platform class.
    
    Provides a unified interface for AI model management, testing,
    monitoring, and orchestration of the entire platform.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        debug: bool = False,
        auto_start: bool = True
    ):
        """
        Initialize the OpenAGI platform.
        
        Args:
            config_path: Path to configuration file
            debug: Enable debug mode
            auto_start: Automatically start platform components
        """
        self.id = str(uuid.uuid4())
        self.started_at = datetime.utcnow()
        self.debug = debug
        
        # Initialize managers
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(self.config.database.to_dict())
        self.auth = AuthenticationManager(self.config.security)
        self.models = ModelRegistry(self.config.models)
        self.testing = SelfTestSuite(self.config.testing)
        self.metrics = MetricsCollector(self.config.monitoring)
        
        # Platform state
        self.active_sessions: Dict[str, Any] = {}
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info(
            "OpenAGI platform initialized", 
            platform_id=self.id,
            debug=debug,
            config_path=config_path
        )
        
        if auto_start:
            asyncio.create_task(self.start())
    
    async def start(self) -> None:
        """Start the OpenAGI platform and all components."""
        logger.info("Starting OpenAGI platform", platform_id=self.id)
        
        try:
            # Initialize database
            await self.db.initialize()
            logger.info("Database initialized")
            
            # Start monitoring
            await self.metrics.start()
            logger.info("Metrics collection started")
            
            # Load default models
            await self.models.load_default_models()
            logger.info("Default models loaded")
            
            # Start background testing if enabled
            if self.config.testing.auto_run:
                task = asyncio.create_task(self._background_testing())
                self.background_tasks.append(task)
                logger.info("Background testing started")
            
            # Start health monitoring
            task = asyncio.create_task(self._health_monitor())
            self.background_tasks.append(task)
            
            logger.info("OpenAGI platform started successfully")
            
        except Exception as e:
            logger.error("Failed to start OpenAGI platform", error=str(e))
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the OpenAGI platform and cleanup resources."""
        logger.info("Stopping OpenAGI platform", platform_id=self.id)
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Cleanup components
        await self.metrics.stop()
        await self.db.close()
        await self.models.cleanup()
        
        logger.info("OpenAGI platform stopped")
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new user session."""
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "models": [],
            "pipelines": [],
            "context": {}
        }
        
        self.active_sessions[session_id] = session
        logger.info("Session created", session_id=session_id, user_id=user_id)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        return self.active_sessions.get(session_id)
    
    async def close_session(self, session_id: str) -> bool:
        """Close a user session."""
        if session_id in self.active_sessions:
            session = self.active_sessions.pop(session_id)
            logger.info("Session closed", session_id=session_id)
            return True
        return False
    
    async def create_pipeline(
        self, 
        models: List[str], 
        session_id: Optional[str] = None
    ) -> str:
        """Create an AI processing pipeline."""
        pipeline_id = str(uuid.uuid4())
        
        # Load models for pipeline
        loaded_models = []
        for model_name in models:
            model = await self.models.get_model(model_name)
            if model:
                loaded_models.append(model)
            else:
                logger.warning("Model not found", model=model_name)
        
        pipeline = {
            "id": pipeline_id,
            "models": loaded_models,
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "usage_count": 0
        }
        
        # Add to session if provided
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id]["pipelines"].append(pipeline_id)
        
        logger.info(
            "Pipeline created", 
            pipeline_id=pipeline_id,
            models=models,
            session_id=session_id
        )
        
        return pipeline_id
    
    async def process(
        self, 
        pipeline_id: str, 
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process inputs through a pipeline."""
        start_time = datetime.utcnow()
        
        try:
            # TODO: Implement actual pipeline processing
            # This is a placeholder that would orchestrate model inference
            result = {
                "pipeline_id": pipeline_id,
                "processed_at": start_time.isoformat(),
                "inputs": inputs,
                "outputs": {"result": "Processed successfully"},
                "processing_time_ms": 100  # Placeholder
            }
            
            # Record metrics
            await self.metrics.record_inference(
                pipeline_id=pipeline_id,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                success=True
            )
            
            logger.info(
                "Pipeline processing completed",
                pipeline_id=pipeline_id,
                processing_time_ms=result["processing_time_ms"]
            )
            
            return result
            
        except Exception as e:
            await self.metrics.record_inference(
                pipeline_id=pipeline_id,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                success=False,
                error=str(e)
            )
            
            logger.error(
                "Pipeline processing failed",
                pipeline_id=pipeline_id,
                error=str(e)
            )
            raise
    
    async def run_tests(
        self, 
        suite: str = "comprehensive",
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run self-tests on the platform."""
        logger.info("Starting test run", suite=suite, models=models)
        
        test_results = await self.testing.run_suite(
            suite_name=suite,
            target_models=models
        )
        
        logger.info(
            "Test run completed",
            suite=suite,
            total_tests=test_results.get("total_tests", 0),
            passed=test_results.get("passed", 0),
            failed=test_results.get("failed", 0)
        )
        
        return test_results
    
    async def get_status(self) -> PlatformStatus:
        """Get current platform status."""
        uptime = datetime.utcnow() - self.started_at
        system_metrics = await self.metrics.get_system_metrics()
        
        return PlatformStatus(
            id=self.id,
            status="running",
            uptime=self.started_at,
            models_loaded=len(await self.models.list_models()),
            tests_running=await self.testing.get_running_tests_count(),
            active_sessions=len(self.active_sessions),
            cpu_usage=system_metrics.get("cpu_percent", 0.0),
            memory_usage=system_metrics.get("memory_percent", 0.0),
            gpu_usage=system_metrics.get("gpu_percent")
        )
    
    async def _background_testing(self) -> None:
        """Run background testing continuously."""
        while True:
            try:
                await asyncio.sleep(self.config.testing.interval_seconds)
                
                if await self.testing.should_run_scheduled():
                    logger.info("Running scheduled background tests")
                    await self.run_tests(suite="scheduled")
                    
            except asyncio.CancelledError:
                logger.info("Background testing cancelled")
                break
            except Exception as e:
                logger.error("Background testing error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _health_monitor(self) -> None:
        """Monitor platform health continuously."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                status = await self.get_status()
                
                # Log health metrics
                logger.info(
                    "Platform health check",
                    cpu_usage=status.cpu_usage,
                    memory_usage=status.memory_usage,
                    active_sessions=status.active_sessions,
                    models_loaded=status.models_loaded
                )
                
                # Check for issues
                if status.cpu_usage > 90:
                    logger.warning("High CPU usage detected", usage=status.cpu_usage)
                
                if status.memory_usage > 90:
                    logger.warning("High memory usage detected", usage=status.memory_usage)
                
            except asyncio.CancelledError:
                logger.info("Health monitoring cancelled")
                break
            except Exception as e:
                logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(60)