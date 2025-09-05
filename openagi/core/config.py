"""Configuration management for OpenAGI platform."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from pydantic import BaseSettings, Field
    from pydantic_settings import BaseSettings as PydanticSettings
except ImportError:
    # Fallback for environments without pydantic
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PydanticSettings(BaseSettings):
        pass
    
    def Field(default=None, **kwargs):
        return default


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "sqlite:///openagi.db")
        self.pool_size = kwargs.get("pool_size", 10)
        self.max_overflow = kwargs.get("max_overflow", 20)
        self.echo = kwargs.get("echo", False)


class RedisConfig(BaseSettings):
    """Redis configuration."""

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 6379)
        self.password = kwargs.get("password", None)
        self.db = kwargs.get("db", 0)


class AIConfig(BaseSettings):
    """AI/ML configuration."""

    def __init__(self, **kwargs):
        self.model_cache_dir = Path(kwargs.get("model_cache_dir", "./models"))
        self.max_model_memory = kwargs.get("max_model_memory", 4096)
        self.device = kwargs.get("device", "auto")
        self.enable_gpu = kwargs.get("enable_gpu", True)


class DebuggingConfig(BaseSettings):
    """Self-debugging configuration."""

    def __init__(self, **kwargs):
        self.enable_auto_debug = kwargs.get("enable_auto_debug", True)
        self.debug_level = kwargs.get("debug_level", 2)
        self.max_debug_history = kwargs.get("max_debug_history", 1000)
        self.enable_self_healing = kwargs.get("enable_self_healing", True)
        self.health_check_interval = kwargs.get("health_check_interval", 30)


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration."""

    def __init__(self, **kwargs):
        self.enable_metrics = kwargs.get("enable_metrics", True)
        self.metrics_port = kwargs.get("metrics_port", 9090)
        self.log_level = kwargs.get("log_level", "INFO")
        log_file = kwargs.get("log_file", None)
        self.log_file = Path(log_file) if log_file else None
        self.enable_prometheus = kwargs.get("enable_prometheus", True)


class APIConfig(BaseSettings):
    """API server configuration."""

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", "127.0.0.1")
        self.port = kwargs.get("port", 8000)
        self.workers = kwargs.get("workers", 4)
        self.reload = kwargs.get("reload", False)
        self.debug = kwargs.get("debug", False)


class OpenAGIConfig(PydanticSettings):
    """Main OpenAGI configuration."""

    def __init__(self, **kwargs: Any) -> None:
        # General settings
        self.app_name = kwargs.get("app_name", "OpenAGI")
        self.app_version = kwargs.get("app_version", "1.0.0")
        self.environment = kwargs.get("environment", "development")
        self.data_dir = Path(kwargs.get("data_dir", "./data"))
        
        # Component configurations
        self.database = DatabaseConfig(**kwargs.get("database", {}))
        self.redis = RedisConfig(**kwargs.get("redis", {}))
        self.ai = AIConfig(**kwargs.get("ai", {}))
        self.debugging = DebuggingConfig(**kwargs.get("debugging", {}))
        self.monitoring = MonitoringConfig(**kwargs.get("monitoring", {}))
        self.api = APIConfig(**kwargs.get("api", {}))

        # Advanced features
        self.enable_distributed = kwargs.get("enable_distributed", False)
        self.enable_clustering = kwargs.get("enable_clustering", False)
        self.security_key = kwargs.get("security_key", "openagi-secret-key")

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [
            self.data_dir,
            self.ai.model_cache_dir,
        ]
        
        if self.monitoring.log_file:
            directories.append(self.monitoring.log_file.parent)
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "data_dir": str(self.data_dir),
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "echo": self.database.echo,
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "password": self.redis.password,
                "db": self.redis.db,
            },
            "ai": {
                "model_cache_dir": str(self.ai.model_cache_dir),
                "max_model_memory": self.ai.max_model_memory,
                "device": self.ai.device,
                "enable_gpu": self.ai.enable_gpu,
            },
            "debugging": {
                "enable_auto_debug": self.debugging.enable_auto_debug,
                "debug_level": self.debugging.debug_level,
                "max_debug_history": self.debugging.max_debug_history,
                "enable_self_healing": self.debugging.enable_self_healing,
                "health_check_interval": self.debugging.health_check_interval,
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "metrics_port": self.monitoring.metrics_port,
                "log_level": self.monitoring.log_level,
                "log_file": str(self.monitoring.log_file) if self.monitoring.log_file else None,
                "enable_prometheus": self.monitoring.enable_prometheus,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
                "reload": self.api.reload,
                "debug": self.api.debug,
            },
            "enable_distributed": self.enable_distributed,
            "enable_clustering": self.enable_clustering,
            "security_key": self.security_key,
        }

    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "OpenAGIConfig":
        """Load configuration from file."""
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            import yaml
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except ImportError:
            raise ImportError("PyYAML is required to load configuration from YAML files")

    def save_to_file(self, config_file: Union[str, Path]) -> None:
        """Save configuration to file."""
        config_file = Path(config_file)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import yaml
            with open(config_file, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except ImportError:
            raise ImportError("PyYAML is required to save configuration to YAML files")