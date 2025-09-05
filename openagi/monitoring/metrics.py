"""
Monitoring and Metrics Collection for OpenAGI Platform

Collects performance metrics, system statistics, and health information.
"""

import asyncio
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """
    Metrics collector for monitoring platform performance.
    
    Collects system metrics, AI model performance, and health statistics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize metrics collector."""
        self.config = config
        self.enabled = config.get("enabled", True)
        self.interval = config.get("metrics_interval", 30)
        self.running = False
        
        # Metrics storage
        self.metrics: Dict[str, Any] = {}
        self.inference_metrics: list = []
        
        logger.info("Metrics collector initialized", enabled=self.enabled)
    
    async def start(self) -> None:
        """Start metrics collection."""
        if not self.enabled:
            return
        
        self.running = True
        logger.info("Starting metrics collection", interval=self.interval)
        
        # Start background collection task
        asyncio.create_task(self._collect_metrics_loop())
    
    async def stop(self) -> None:
        """Stop metrics collection."""
        self.running = False
        logger.info("Metrics collection stopped")
    
    async def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_avg": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
            return {"timestamp": time.time()}
    
    async def record_inference(
        self,
        pipeline_id: str,
        processing_time: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Record inference metrics."""
        metric = {
            "pipeline_id": pipeline_id,
            "processing_time": processing_time,
            "success": success,
            "error": error,
            "timestamp": time.time()
        }
        
        self.inference_metrics.append(metric)
        
        # Keep only recent metrics (last 1000)
        if len(self.inference_metrics) > 1000:
            self.inference_metrics = self.inference_metrics[-1000:]
    
    async def _collect_metrics_loop(self) -> None:
        """Background metrics collection loop."""
        while self.running:
            try:
                system_metrics = await self.get_system_metrics()
                self.metrics.update(system_metrics)
                
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in metrics collection loop", error=str(e))
                await asyncio.sleep(self.interval)