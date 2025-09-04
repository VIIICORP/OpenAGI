"""Core platform implementation for OpenAGI."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..models.registry import ModelRegistry
from ..agents.manager import AgentManager
from ..storage.manager import StorageManager
from ..monitoring.metrics import MetricsCollector
from .config import Config

logger = logging.getLogger(__name__)


class OpenAGI:
    """
    Main OpenAGI platform class that orchestrates all AI models and features.
    
    This class serves as the central hub for accessing 20,000+ AI models,
    managing agents, handling storage, and monitoring system performance.
    
    Attributes:
        models: ModelRegistry for managing AI models
        agents: AgentManager for autonomous agents  
        storage: StorageManager for data persistence
        metrics: MetricsCollector for monitoring
        config: Configuration management
    """
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        Initialize the OpenAGI platform.
        
        Args:
            config_path: Path to configuration file
            **kwargs: Additional configuration options
        """
        self.config = Config(config_path, **kwargs)
        
        # Initialize core components
        self._setup_logging()
        self.models = ModelRegistry(self.config)
        self.agents = AgentManager(self.config, self.models)
        self.storage = StorageManager(self.config)
        self.metrics = MetricsCollector(self.config)
        
        logger.info("OpenAGI platform initialized successfully")
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get("logging.level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
    def list_categories(self) -> Dict[str, int]:
        """
        List all available model categories and their counts.
        
        Returns:
            Dictionary mapping category names to model counts
        """
        return self.models.list_categories()
        
    def search_models(self, query: str, category: Optional[str] = None) -> list:
        """
        Search for models by name, description, or tags.
        
        Args:
            query: Search query string
            category: Optional category filter
            
        Returns:
            List of matching model definitions
        """
        return self.models.search(query, category)
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get platform statistics including model counts and usage metrics.
        
        Returns:
            Dictionary containing platform statistics
        """
        return {
            "total_models": self.models.count(),
            "categories": self.models.list_categories(),
            "active_agents": self.agents.count_active(),
            "storage_usage": self.storage.get_usage(),
            "system_metrics": self.metrics.get_current()
        }
        
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the platform.
        
        Returns:
            Health status of all components
        """
        return {
            "status": "healthy",
            "models": self.models.health_check(),
            "agents": self.agents.health_check(), 
            "storage": self.storage.health_check(),
            "metrics": self.metrics.health_check()
        }
        
    def shutdown(self):
        """Gracefully shutdown the platform."""
        logger.info("Shutting down OpenAGI platform")
        self.agents.shutdown_all()
        self.storage.close()
        self.metrics.stop()
        logger.info("OpenAGI platform shutdown complete")